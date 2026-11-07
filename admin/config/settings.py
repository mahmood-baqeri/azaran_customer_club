import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

####################################
##            Setting            ##
####################################
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend_files'

# خواندن SECRET_KEY از متغیر محیطی
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# خواندن DEBUG از متغیر محیطی (پیش‌فرض: False)
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['www.hrclub.azaran.group', 'hrclub.azaran.group', 'localhost', '127.0.0.1']

AUTH_USER_MODEL = "app_user.User"
ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

VAPID_PUBLIC_KEY = "BPuKbxalvYwmtIqaT9bcso9gl-szwU_6a0D3NwzBbCoSVrYlSscSYbQZ0-txmQ31h8jELnOb-2PurnE6IKO3kRg"
VAPID_PRIVATE_KEY = "KjyKzXUy8Rfr5ZCDcOSV_h5WNEByfkfLPggQk2lvGEc"
VAPID_CLAIMS = {
    "sub": "mailto:azaraninfo@azaran-group.com"
}

####################################
##            Application           ##
####################################
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",

    'tinymce',
    'jalali_date',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'axes',
    'django_filters', 

    'applications.log.apps.config',
    'applications.category.apps.config',
    'applications.page.apps.config',
    'applications.role.apps.config',
    'applications.setting.apps.config',
    'applications.user.apps.config',
    'applications.gift.apps.config',
    'applications.promotion.apps.config',
    'applications.faq.apps.config',
    'applications.score.apps.config',
    'applications.factor.apps.config',
    'applications.project.apps.config',
    'applications.support.apps.config',
]

####################################
##            MIDDLEWARE           ##
####################################
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'applications.log.middleware.RequestLogMiddleware',
]

####################################
##            Database            ##
####################################
DEVELOPMENT = os.environ.get('DEVELOPMENT', 'local')
if DEVELOPMENT == 'server':
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'NAME': os.environ.get('DB_NAME', ''),
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'localhost',
            'PORT': '3306',
            'NAME': 'azar_customer',
            'USER': 'root',
            'PASSWORD': '',
        }
    }

####################################
##      Password validation       ##
####################################
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

####################################
##      CELERY      ##
####################################
CELERY_BROKER_URL = 'redis://:Jasper81402T9vR3kL8qP2xZ7sM2025@localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://:Jasper81402T9vR3kL8qP2xZ7sM2025@localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'

CELERY_BEAT_SCHEDULE = {
    # 'task_1': {
    #     'task': 'tasks.tasks.evaluation',
    #     'schedule': crontab(minute='*/10'),
    # },
    # 'task_2': {
    #     'task': 'tasks.tasks.personnel',
    #     'schedule': crontab(hour=23, minute=0),
    # },
}

####################################
##             DEBUG             ##
####################################
if DEBUG:
    CACHE_MIDDLEWARE_SECONDS = 0
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    INSTALLED_APPS += ['debug_toolbar', 'django_dump_die']
    MIDDLEWARE += [
        'django_dump_die.middleware.DumpAndDieMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

####################################
##            TEMPLATES           ##
####################################
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates/',
            FRONTEND_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "applications.core.processors.sitSettings",
                "applications.core.processors.adminAccess",
                "applications.core.processors.adminNotifications",
                "applications.core.processors.checkActiveModule",
            ],
            'libraries': {
                'customTags': 'applications.core.tags',
            }
        },
    },
]

####################################
##             STATIC             ##
####################################
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static_files",
]
STATIC_ROOT = BASE_DIR / "static_root"

REACT_ASSETS_URL = '/assets/'
REACT_ASSETS_DIR = FRONTEND_DIR / 'assets'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "static_media"

####################################
##             LOGGING            ##
####################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'applications.log': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

####################################
##         REST FRAMEWORK         ##
####################################
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    
    # 👇 اضافه کن:
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1000),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

####################################
##  CORS ##
####################################
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

CORS_ALLOWED_ORIGINS = [
    "https://hrclub.azaran-group.com",
    "https://www.hrclub.azaran-group.com",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_TRUSTED_ORIGINS = [
    "https://hrclub.azaran-group.com",
    "https://www.hrclub.azaran-group.com",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

# 👇 کامل شد
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-action",
    "x-requested-with",
    "x-csrftoken",
]

####################################
##       امنیت پیشرفته (سشن، رمز، هدرها)      ##
####################################

# --- امنیت سشن: 1 روز ---
SESSION_COOKIE_AGE = 86400
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False        # 👈 سبک‌تر


# --- هدرهای امنیتی HTTP ---
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- محدودیت تلاش‌های ورود (django-axes) ---
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True