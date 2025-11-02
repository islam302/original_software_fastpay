import os
from datetime import timedelta
from pathlib import Path
from typing import Dict, List

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, []),
)
env.escape_proxy = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = env("DEBUG")

ALLOWED_HOSTS: List[str] = env("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # packages
    "rest_framework",
    "rest_framework.authtoken",
    "allauth.account",
    "dj_rest_auth.registration",
    "allauth.socialaccount",
    "drf_yasg",
    "smart_selects",
    "nested_admin",
    "phonenumber_field",
    "constance",
    "constance.backends.database",
    "django_cleanup.apps.CleanupConfig",
    "django_json_widget",
    # local apps
    "authentication",
    "products",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "crum.CurrentRequestUserMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
]


# Custom Usert Model
AUTH_USER_MODEL = "authentication.User"

# Custom Login Model

REST_AUTH_SERIALIZERS = {
    "LOGIN_SERIALIZER": "authentication.serializers.CustomLoginSerializer",
}

REST_USE_JWT = True
JWT_AUTH_COOKIE = "original-softwere-fib-website-jwt"
JWT_AUTH_REFRESH_COOKIE = "original-softwere-fib-jwt-refresh"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=86400),
}


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'core.utils.CustomJSONRenderer',  # Replace with the actual path
        'rest_framework.renderers.BrowsableAPIRenderer',  # Optional, for API browsing
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler',
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "COERCE_DECIMAL_TO_STRING": False,
    "PAGE_SIZE": 10,
}


ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"  # "mandatory", "optional", or "none"
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_USERNAME_REQUIRED = True


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Baghdad"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "https://fastpay.tlmozan.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of allauth
    "django.contrib.auth.backends.ModelBackend",
    # allauth specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

# django-corsheaders
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ["*"]
# CORS_ALLOWED_ORIGINS = [
# ]

# drf_yasg
SWAGGER_SETTINGS = {
    # "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    "LOGOUT_URL": "/admin/logout/",
}
