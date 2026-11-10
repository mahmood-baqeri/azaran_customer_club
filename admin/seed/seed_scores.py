# admin/seed/seed_scores.py

import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # این همان پوشه admin/ است
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from applications.user.models import User
from applications.score.models import UserScore, UserScoreLog
from django.db import transaction

def seed_fake_data():
    user_id = 1
    
    if not User.objects.filter(id=user_id).exists():
        print(f"❌ کاربر با آیدی {user_id} یافت نشد!")
        return

    print(f"⏳ در حال تولید داده‌های فیک برای کاربر {user_id}...")

    with transaction.atomic():
        # ۱. پاکسازی داده‌های قبلی
        UserScoreLog.objects.filter(user_id=user_id).delete()
        UserScore.objects.filter(user_id=user_id).delete()

        # ۲. ساخت رکورد امتیاز
        score = UserScore.objects.create(user_id=user_id, current_balance=0, total_earned=0, total_spent=0)

        # ۳. لیست کدهای کسب و خرج
        earn_codes = [
            UserScoreLog.TransactionCode.SIGNUP, UserScoreLog.TransactionCode.PROFILE_PERSONAL_INFO,
            UserScoreLog.TransactionCode.INVOICE, UserScoreLog.TransactionCode.REFERRAL,
            UserScoreLog.TransactionCode.DAILY_QUIZ, UserScoreLog.TransactionCode.TREASURE_HUNT,
            UserScoreLog.TransactionCode.FORTUNE_WHEEL, UserScoreLog.TransactionCode.SURVEY,
            UserScoreLog.TransactionCode.QA_ANSWER, UserScoreLog.TransactionCode.GALLERY_TOP
        ]
        spend_codes = [
            UserScoreLog.TransactionCode.GIFT_REDEEM, UserScoreLog.TransactionCode.CUSTOM_GIFT,
            UserScoreLog.TransactionCode.EXPIRE
        ]

        now = timezone.now()
        fake_logs = []
        
        # ۴. تولید ۵۰ تراکنش تصادفی در ۶ ماه گذشته
        for _ in range(50):
            random_days = random.randint(0, 180)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            log_date = now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

            if random.random() < 0.7:
                code = random.choice(earn_codes)
                direction = UserScoreLog.Direction.EARNED
                amount = random.randint(10, 500)
            else:
                code = random.choice(spend_codes)
                direction = UserScoreLog.Direction.SPENT
                amount = random.randint(50, 300)

            source = random.choice(UserScoreLog.Source.values)
            is_reversed = random.choice([True, False, False, False])

            fake_logs.append({
                "date": log_date,
                "code": code,
                "direction": direction,
                "amount": amount,
                "source": source,
                "is_reversed": is_reversed
            })

        # ۵. مرتب‌سازی زمانی
        fake_logs.sort(key=lambda x: x["date"])

        # ۶. محاسبه موجودی و درج در دیتابیس
        current_balance = 0
        total_earned = 0
        total_spent = 0

        for log in fake_logs:
            balance_before = current_balance
            
            if log["direction"] == UserScoreLog.Direction.EARNED:
                current_balance += log["amount"]
                total_earned += log["amount"]
            else:
                current_balance -= log["amount"]
                total_spent += log["amount"]

            if current_balance < 0:
                current_balance = 0

            # ساخت لاگ
            db_log = UserScoreLog.objects.create(
                user_id=user_id,
                transaction_code=log["code"],
                direction=log["direction"],
                amount=log["amount"],
                balance_before=balance_before,
                balance_after=current_balance,
                source=log["source"],
                is_reversed=log["is_reversed"],
                reason="داده تستی (Seeder)",
                extra_data={"is_fake": True}
            )

            # 👈 چون created_at معمولا auto_now_add است، این خط تاریخ را دستی جایگزین میکند
            UserScoreLog.objects.filter(id=db_log.id).update(created_at=log["date"])

        # ۷. آپدیت موجودی نهایی
        score.current_balance = current_balance
        score.total_earned = total_earned
        score.total_spent = total_spent
        score.save(update_fields=["current_balance", "total_earned", "total_spent"])

        print("✅ داده‌های فیک با موفقیت ثبت شدند!")
        print(f"📊 تعداد تراکنش‌ها: 50")
        print(f"💰 موجودی نهایی: {current_balance}")
        print(f"📈 کل کسب شده: {total_earned}")
        print(f"📉 کل خرج شده: {total_spent}")


if __name__ == "__main__":
    seed_fake_data()