
import os
import re
import sys
import uuid
import argparse
import logging

from pathlib import Path
from datetime import datetime

# ============================================================
# 1. DJANGO CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django
django.setup()

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import is_password_usable

from applications.user.models import User, UserProfile


# ============================================================
# 2. CONFIGURATION
# ============================================================

SQL_FILE = BASE_DIR / "users.sql"

REPORT_DIR = BASE_DIR / "migration_reports"

BATCH_SIZE = 200

# در صورت نیاز به توقف بعد از تعداد مشخصی خطا
MAX_ERRORS = 1000

REPORT_DIR.mkdir(exist_ok=True)

LOG_FILE = REPORT_DIR / "migration.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger("user_migration")


# ============================================================
# 3. STATISTICS
# ============================================================

stats = {
    "total": 0,
    "valid_mobile": 0,
    "invalid_mobile": 0,
    "created": 0,
    "updated": 0,
    "profiles_created": 0,
    "profiles_updated": 0,
    "skipped": 0,
    "errors": 0,
}


# ============================================================
# 4. SQL PARSER
# ============================================================

MYSQL_ESCAPES = {
    "0": "\0",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


def parse_sql_value(sql, position):
    """
    Parse one MySQL SQL value.
    Supports quoted strings, escaped characters and NULL.
    """

    length = len(sql)

    while position < length and sql[position].isspace():
        position += 1

    if position >= length:
        raise ValueError("Unexpected end of SQL value")

    # Quoted string
    if sql[position] in ("'", '"'):

        quote = sql[position]
        position += 1

        result = []

        while position < length:

            char = sql[position]

            if char == "\\":
                position += 1

                if position >= length:
                    raise ValueError("Invalid escape sequence")

                escaped = sql[position]

                result.append(
                    MYSQL_ESCAPES.get(escaped, escaped)
                )

                position += 1
                continue

            if char == quote:

                # SQL doubled quote
                if (
                    position + 1 < length
                    and sql[position + 1] == quote
                ):
                    result.append(quote)
                    position += 2
                    continue

                position += 1
                return "".join(result), position

            result.append(char)
            position += 1

        raise ValueError("Unclosed SQL string")

    # Numeric, NULL or other unquoted values
    start = position

    while position < length and sql[position] not in ",)":
        position += 1

    value = sql[start:position].strip()

    if value.upper() == "NULL":
        return None, position

    if value.upper() == "TRUE":
        return True, position

    if value.upper() == "FALSE":
        return False, position

    if re.fullmatch(r"-?\d+", value):
        return int(value), position

    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value), position

    return value, position


def extract_insert_statement(sql, start):
    """
    Extract one complete INSERT statement.
    Semicolons inside quoted strings are ignored.
    """

    quote = None
    escaped = False

    for position in range(start, len(sql)):

        char = sql[position]

        if escaped:
            escaped = False
            continue

        if quote:

            if char == "\\":
                escaped = True

            elif char == quote:
                quote = None

            continue

        if char in ("'", '"'):
            quote = char

        elif char == ";":
            return sql[start:position], position + 1

    return sql[start:], len(sql)


def parse_insert_rows(statement):
    """
    Parse rows inside INSERT INTO ... VALUES.
    """

    values_match = re.search(
        r"\bVALUES\b",
        statement,
        re.IGNORECASE
    )

    if not values_match:
        return

    sql = statement[values_match.end():]

    position = 0
    length = len(sql)

    while position < length:

        while (
            position < length
            and sql[position] in " \r\n\t,"
        ):
            position += 1

        if position >= length:
            break

        if sql[position] != "(":
            break

        position += 1

        row = []

        while position < length:

            while (
                position < length
                and sql[position].isspace()
            ):
                position += 1

            if position < length and sql[position] == ")":
                position += 1
                break

            value, position = parse_sql_value(
                sql,
                position
            )

            row.append(value)

            while (
                position < length
                and sql[position].isspace()
            ):
                position += 1

            if position >= length:
                break

            if sql[position] == ",":
                position += 1
                continue

            if sql[position] == ")":
                position += 1
                break

            raise ValueError(
                f"Unexpected SQL character: {sql[position]}"
            )

        yield row


def extract_users_from_sql(file_path):
    """
    Read users from SQL dump.
    Supports multiple INSERT statements.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {file_path}"
        )

    logger.info("Reading SQL file: %s", file_path)

    content = file_path.read_text(
        encoding="utf-8-sig"
    )

    pattern = re.compile(
        r"INSERT\s+INTO\s+`?users`?\s*\(",
        re.IGNORECASE
    )

    records = []
    insert_count = 0

    for match in pattern.finditer(content):

        # Extract column definitions
        open_position = match.end() - 1
        close_position = content.find(")", open_position)

        if close_position == -1:
            logger.warning("Invalid INSERT columns")
            continue

        columns_part = content[
            open_position + 1:close_position
        ]

        columns = [
            item.strip().strip("`").strip()
            for item in columns_part.split(",")
        ]

        # Extract complete INSERT statement
        statement, _ = extract_insert_statement(
            content,
            close_position + 1
        )

        try:

            for row in parse_insert_rows(statement):

                if len(row) != len(columns):

                    logger.warning(
                        "Column count mismatch: %s != %s",
                        len(columns),
                        len(row)
                    )

                    continue

                records.append(
                    dict(zip(columns, row))
                )

            insert_count += 1

        except Exception as error:

            logger.error(
                "INSERT parsing error: %s",
                error
            )

    logger.info(
        "SQL parsing completed. INSERT statements: %s | Records: %s",
        insert_count,
        len(records)
    )

    return records


# ============================================================
# 5. DATA NORMALIZATION
# ============================================================

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def normalize_digits(value):

    if value is None:
        return ""

    value = str(value).translate(
        str.maketrans(
            PERSIAN_DIGITS + ARABIC_DIGITS,
            "0123456789" * 2
        )
    )

    return value


def clean_mobile(value):

    value = normalize_digits(value).strip()

    # Remove common separators
    value = re.sub(r"[\s\-()]", "", value)

    return value


def valid_mobile(value):

    return bool(
        re.fullmatch(r"09\d{9}", clean_mobile(value))
    )


def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


def clean_optional(value):

    value = clean_text(value)

    return value if value else None


def parse_datetime(value):

    if not value:
        return None

    value = str(value).strip()

    if value.startswith("0000-00-00"):
        return None

    try:

        result = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if timezone.is_naive(result):
            result = timezone.make_aware(result)

        return result

    except (ValueError, TypeError):
        return None


# ============================================================
# 6. USER MAPPING
# ============================================================

def map_job_type_to_nature(job_type):

    mapping = {
        "0": "seller",
        "1": "executive",
        "2": "user",
        "3": "user",
        "4": "user",
    }

    return mapping.get(
        str(job_type).strip(),
        "user"
    )


def get_unique_username(old_username, mobile):

    username_field = User._meta.get_field("username")

    max_length = username_field.max_length or 150

    candidate = clean_text(old_username)

    if not candidate:
        candidate = mobile

    candidate = candidate[:max_length]

    existing = User.objects.filter(
        username=candidate
    ).first()

    if not existing:
        return candidate

    # Keep existing user's username if it belongs to them
    if existing.mobile == mobile:
        return candidate

    base = f"legacy_{mobile}"[:max_length]

    candidate = base
    counter = 1

    while User.objects.filter(username=candidate).exclude(
        mobile=mobile
    ).exists():

        suffix = f"_{counter}"

        candidate = (
            base[:max_length - len(suffix)] + suffix
        )

        counter += 1

    return candidate


def get_unique_email(old_email, mobile):

    email = clean_text(old_email)

    email_field = User._meta.get_field("email")
    max_length = email_field.max_length or 254

    if not email:
        email = f"{mobile}@legacy.invalid"

    email = email[:max_length]

    # Standard Django AbstractUser email is not unique.
    # Check uniqueness only when the actual model requires it.
    if not email_field.unique:
        return email

    existing = User.objects.filter(email=email).first()

    if not existing or existing.mobile == mobile:
        return email

    base = f"{mobile}@legacy.invalid"

    candidate = base[:max_length]
    counter = 1

    while User.objects.filter(email=candidate).exclude(
        mobile=mobile
    ).exists():

        suffix = f".{counter}"

        candidate = (
            f"{mobile[:max_length - len(suffix) - 15]}"
            f"{suffix}@legacy.invalid"
        )

        counter += 1

    return candidate


def get_valid_uuid(value, current_user=None):

    if value:

        try:
            parsed = uuid.UUID(str(value).strip())

            duplicate = User.objects.filter(
                uuid=parsed
            )

            if current_user:
                duplicate = duplicate.exclude(
                    pk=current_user.pk
                )

            if not duplicate.exists():
                return parsed

        except (ValueError, TypeError, AttributeError):
            pass

    if current_user and current_user.uuid:
        return current_user.uuid

    while True:

        generated = uuid.uuid4()

        if not User.objects.filter(uuid=generated).exists():
            return generated


# ============================================================
# 7. FOREIGN KEY VALIDATION
# ============================================================

def get_valid_fk_id(model, field_name, raw_value):

    if raw_value is None:
        return None

    value = str(raw_value).strip()

    if not value:
        return None

    try:

        field = model._meta.get_field(field_name)

        related_model = field.remote_field.model

        converted = related_model._meta.pk.to_python(value)

        if related_model.objects.filter(
            pk=converted
        ).exists():

            return converted

        logger.warning(
            "Invalid FK: %s=%s",
            field_name,
            value
        )

        return None

    except Exception as error:

        logger.warning(
            "FK validation failed: %s=%s | %s",
            field_name,
            value,
            error
        )

        return None


# ============================================================
# 8. NATIONAL CODE VALIDATION
# ============================================================

def get_valid_national_code(value, user):

    code = normalize_digits(value).strip()

    if not code:
        return None

    # Destination field has max_length=10
    if not re.fullmatch(r"\d{10}", code):
        logger.warning(
            "Invalid national code for mobile %s",
            user.mobile
        )
        return None

    duplicate = UserProfile.objects.filter(
        national_code=code
    ).exclude(
        user=user
    )

    if duplicate.exists():

        logger.warning(
            "Duplicate national code: %s | mobile: %s",
            code,
            user.mobile
        )

        return None

    return code


# ============================================================
# 9. PASSWORD MIGRATION
# ============================================================

def migrate_password(raw_password):

    if not raw_password:
        return None

    password = str(raw_password).strip()

    # Laravel bcrypt hashes start with $2y$.
    # Django BCryptPasswordHasher expects bcrypt$ prefix.
    if password.startswith(("$2y$", "$2a$", "$2b$")):
        return "bcrypt$" + password

    # Preserve existing Django encoded passwords
    if "$" in password:
        return password

    return None


# ============================================================
# 10. PROCESS ONE USER
# ============================================================

def process_user(data, dry_run=False):

    mobile = clean_mobile(data.get("mobile"))

    if not valid_mobile(mobile):

        stats["invalid_mobile"] += 1
        stats["skipped"] += 1

        return

    stats["valid_mobile"] += 1

    with transaction.atomic():

        user = User.objects.filter(
            mobile=mobile
        ).first()

        created = user is None

        if dry_run:

            if created:
                stats["created"] += 1
            else:
                stats["updated"] += 1

            return

        if created:
            user = User(mobile=mobile)

        # ------------------------------------------
        # User fields
        # ------------------------------------------

        user.username = get_unique_username(
            data.get("username"),
            mobile
        )

        user.first_name = clean_text(
            data.get("firstName")
        )[:150]

        user.last_name = clean_text(
            data.get("lastName")
        )[:150]

        user.email = get_unique_email(
            data.get("email"),
            mobile
        )

        user.is_active = str(
            data.get("status") or ""
        ).strip() == "1"

        user.nature = map_job_type_to_nature(
            data.get("jopType")
        )

        user.uuid = get_valid_uuid(
            data.get("uuid"),
            user if not created else None
        )

        # Preserve old password hash
        password = migrate_password(
            data.get("password")
        )

        if password:
            user.password = password

        elif created:
            user.set_unusable_password()

        # Save user
        user.save()

        # Preserve last_online because last_active_at
        # has auto_now=True in the Django model.
        last_online = parse_datetime(
            data.get("last_online")
        )

        if last_online:

            User.objects.filter(
                pk=user.pk
            ).update(
                last_active_at=last_online
            )

        # ------------------------------------------
        # User profile
        # ------------------------------------------

        national_code = get_valid_national_code(
            data.get("national_code"),
            user
        )

        province_id = get_valid_fk_id(
            UserProfile,
            "province",
            data.get("state_id")
        )

        city_id = get_valid_fk_id(
            UserProfile,
            "city",
            data.get("city_id")
        )

        profile_defaults = {

            "national_code": national_code,

            "address": clean_optional(
                data.get("address")
            ),

            "post_code": clean_optional(
                data.get("postcode")
            ),

            "province_id": province_id,

            "city_id": city_id,

            "job_title": clean_optional(
                data.get("jopType")
            ),
        }

        profile, profile_created = (
            UserProfile.objects.update_or_create(
                user=user,
                defaults=profile_defaults
            )
        )

        # ------------------------------------------
        # Statistics
        # ------------------------------------------

        if created:
            stats["created"] += 1
        else:
            stats["updated"] += 1

        if profile_created:
            stats["profiles_created"] += 1
        else:
            stats["profiles_updated"] += 1


# ============================================================
# 11. MAIN MIGRATION
# ============================================================

def migrate(dry_run=False):

    logger.info("=" * 60)
    logger.info("USER MIGRATION STARTED")
    logger.info("DRY RUN: %s", dry_run)
    logger.info("=" * 60)

    users_data = extract_users_from_sql(SQL_FILE)

    stats["total"] = len(users_data)

    logger.info(
        "Total source records: %s",
        stats["total"]
    )

    for index, data in enumerate(users_data, start=1):

        if stats["errors"] >= MAX_ERRORS:

            logger.error(
                "Maximum error limit reached. Stopping."
            )

            break

        try:

            process_user(
                data,
                dry_run=dry_run
            )

        except Exception as error:

            stats["errors"] += 1

            logger.exception(
                "Record failed | ID: %s | Mobile: %s | Error: %s",
                data.get("id"),
                data.get("mobile"),
                error
            )

        if index % BATCH_SIZE == 0:

            logger.info(
                "Progress: %s / %s | Created: %s | Updated: %s | Errors: %s",
                index,
                stats["total"],
                stats["created"],
                stats["updated"],
                stats["errors"]
            )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    logger.info("=" * 60)
    logger.info("MIGRATION FINAL REPORT")
    logger.info("=" * 60)

    for key, value in stats.items():

        logger.info("%-22s : %s", key, value)

    logger.info("=" * 60)

    report_file = REPORT_DIR / "migration_report.txt"

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as report:

        report.write("USER MIGRATION REPORT\n")
        report.write("=" * 50 + "\n\n")

        report.write(
            f"Mode: {'DRY RUN' if dry_run else 'REAL MIGRATION'}\n\n"
        )

        for key, value in stats.items():

            report.write(
                f"{key}: {value}\n"
            )

        report.write("\n")
        report.write(
            f"Finished at: {timezone.now()}\n"
        )

    logger.info(
        "Report saved: %s",
        report_file
    )


# ============================================================
# 12. ENTRY POINT
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Migrate Laravel users to Django"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate records without changing destination database"
    )

    args = parser.parse_args()

    migrate(
        dry_run=args.dry_run
    )
