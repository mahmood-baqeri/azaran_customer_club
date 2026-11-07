# applications/_fastapi/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "6R6wjk8o2RYKh_-eBvZ2mdsasFGADSOPI_sdCASD4bbFSDFbs8t3az6uWAv_kP_XkXYuZzGq0TRHEaslkrnQNEWNknqNL0RJpBQxAi9j6bM-ZgpIg")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "14400"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

# تنظیمات rate-limit
FORGET_RATE_LIMIT_KEY = "forget_rate_{email}"
FORGET_RATE_LIMIT_KEY_PHONE = "forget_rate_phone_{mobile}"
FORGET_RATE_LIMIT_SECONDS = 60  # یک درخواست فراموشی در هر 60 ثانیه برای هر ایمیل
VERIFY_MAX_ATTEMPTS: int = 5  # دفعات مجاز برای وارد کردن کد اشتباه


# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_DAY = int(os.getenv("RATE_LIMIT_PER_DAY", "1000"))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")