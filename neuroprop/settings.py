from pathlib import Path
import os
import environ
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import logging

def get_list(text):
    return [item.strip() for item in text.split(",")]

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = get_list(env("ALLOWED_HOSTS"))

SIGNUP_ACCESS_CODE = os.getenv('SIGNUP_ACCESS_CODE')

TREPP_API_USERNAME = env("TREPP_API_USERNAME", default="sam@dim3nsion.co")
TREPP_API_PASSWORD = env("TREPP_API_PASSWORD", default="Treppdata2023$")

if not SIGNUP_ACCESS_CODE:
    raise ImproperlyConfigured("SIGNUP_ACCESS_CODE environment variable is not set")

GOOGLE_MAPS_API_KEY = 'AIzaSyBMZNsxqP3f8gzuum4bTtUGTo2IUV4it20'

SUPPORT_EMAIL = 'sean@neuroprop.com'  

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'core',
    'prospect',
    'widget_tweaks',
    'tracker',
    'market',
    'sync',
    'jsonify',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.account_allowed',
]

ROOT_URLCONF = 'neuroprop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'neuroprop.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'NAME': env("DB_NAME"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_HOST_USER = "sam@dim3nsion.co"
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = "NeuroProp <sam@dim3nsion.co>"
    
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'


STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

AUTH_USER_MODEL = "account.User"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_ASSISTANT_UNDERWRITE_ID = "asst_WOV9oHdjiS0zGbiPgBrXIVyn"
OPENAI_ASSISTANT_FILE_CHECK_ID = "asst_5kPKg5hT7z4t3qJda2dpu1DL"
OPENAI_ASSISTANT_MASTER_ID = "asst_DeuBJn5T8Qqqv61ptoDgHOsk"

OPENAI_DOC_FEEDBACK_ID = "asst_WWN8Bci3dz1aYj2QdEjENBnW"
OPENAI_OUTREACH_ID = "asst_cavesOYRchqcdXq0BWSa4Nu7"
OPENAI_DOC_SORT_ID = "asst_uVtUUVvCAB1TWU3Ebecu3QA5"
# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACKS_LATE = True

GOOGLE_MAPS_API_KEY="AIzaSyAAjzSqYKYNaBs-XM7fnh1-KrvBfy-Cwpc"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}