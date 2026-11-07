from __future__ import absolute_import, unicode_literals
import os
import sys
from pathlib import Path
from celery import Celery

# اضافه کردن مسیر ریشه پروژه به PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# تنظیم پروژه Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ایجاد شیء Celery
app = Celery('config')

# پیکربندی Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# شناسایی task‌ها
app.autodiscover_tasks(['tasks'])
