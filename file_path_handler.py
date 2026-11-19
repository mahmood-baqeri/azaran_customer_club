
from pathlib import Path


# ==========================================
# Project Configuration
# ==========================================

# پوشه اصلی پروژه (کنار فایل اجرایی)
PROJECT_DIR = Path(__file__).parent / "admin"


# پوشه‌هایی که نباید وارد آن‌ها شویم
IGNORE_DIRS = {
    ".venv",
    "venv",
    "migrations",
    "env",
    "node_modules",
    ".next",
    ".vscode",
    ".git",
    ".idea",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


# ==========================================
# Comment Styles
# ==========================================

COMMENT_STYLES = {

    # Python / Shell / Config
    ".py": ("# ", ""),
    ".pyw": ("# ", ""),
    ".sh": ("# ", ""),
    ".bash": ("# ", ""),
    ".yml": ("# ", ""),
    ".yaml": ("# ", ""),
    ".toml": ("# ", ""),
    ".ini": ("# ", ""),
    ".cfg": ("# ", ""),
    ".conf": ("# ", ""),
    ".env": ("# ",),

    # JavaScript / TypeScript / Programming
    ".js": ("// ", ""),
    ".jsx": ("// ", ""),
    ".ts": ("// ", ""),
    ".tsx": ("// ", ""),
    ".mjs": ("// ", ""),
    ".cjs": ("// ", ""),
    ".java": ("// ", ""),
    ".c": ("// ", ""),
    ".cpp": ("// ", ""),
    ".h": ("// ", ""),
    ".hpp": ("// ", ""),
    ".cs": ("// ", ""),
    ".go": ("// ", ""),
    ".rs": ("// ", ""),
    ".php": ("// ", ""),
    ".swift": ("// ", ""),
    ".kt": ("// ", ""),
    ".dart": ("// ",),
    
    # CSS
    ".css": ("/* ", " */"),
    ".scss": ("/* ", " */"),
    ".less": ("/* ", " */"),

    # HTML / XML
    ".html": ("<!-- ", " -->"),
    ".htm": ("<!-- ", " -->"),
    ".xml": ("<!-- ", " -->"),
    ".svg": ("<!-- ", " -->"),

    # SQL
    ".sql": ("-- ", ""),

    # Other
    ".lua": ("-- ", ""),
    ".rb": ("# ", ""),
    ".r": ("# ", ""),
    ".pl": ("# ", ""),
}


# ==========================================
# File Processing
# ==========================================

def process_file(file_path: Path):

    suffix = file_path.suffix.lower()

    if suffix not in COMMENT_STYLES:
        return False

    comment_style = COMMENT_STYLES[suffix]

    prefix = comment_style[0]
    postfix = comment_style[1] if len(comment_style) > 1 else ""

    try:

        # Read file
        content = file_path.read_text(encoding="utf-8")

        # Relative path
        relative_path = file_path.relative_to(
            PROJECT_DIR
        ).as_posix()

        marker = f"Path: {relative_path}"

        # Avoid duplicate path
        if content.startswith(prefix + marker):
            print(f"[SKIP] {relative_path}")
            return False

        # Create comment
        comment = f"{prefix}{marker}{postfix}"

        # Add comment at beginning
        new_content = comment + "\n\n" + content

        # Write file
        file_path.write_text(
            new_content,
            encoding="utf-8",
            newline=""
        )

        print(f"[OK] {relative_path}")

        return True

    except UnicodeDecodeError:
        print(f"[SKIP - BINARY/ENCODING] {file_path}")
        return False

    except Exception as error:
        print(f"[ERROR] {file_path}: {error}")
        return False


# ==========================================
# Project Scanner
# ==========================================

def scan_project():

    if not PROJECT_DIR.exists():

        print("[ERROR] Project directory not found!")
        print(f"Path: {PROJECT_DIR}")

        return

    print("=" * 60)
    print("PROJECT FILE PATH INJECTOR")
    print("=" * 60)

    print(f"Project: {PROJECT_DIR}")
    print("-" * 60)

    scanned = 0
    modified = 0
    skipped = 0

    # Recursive scan
    for file_path in PROJECT_DIR.rglob("*"):

        # Ignore excluded directories at any depth
        relative_parts = file_path.relative_to(
            PROJECT_DIR
        ).parts

        if any(part in IGNORE_DIRS for part in relative_parts):
            continue

        if not file_path.is_file():
            continue

        scanned += 1

        if process_file(file_path):
            modified += 1
        else:
            skipped += 1

    print("-" * 60)

    print(f"Total scanned : {scanned}")
    print(f"Modified      : {modified}")
    print(f"Skipped       : {skipped}")

    print("=" * 60)
    print("PROCESS COMPLETED")
    print("=" * 60)


# ==========================================
# Entry Point
# ==========================================

if __name__ == "__main__":

    scan_project()
