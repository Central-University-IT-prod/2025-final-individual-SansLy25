import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from gigachat import GigaChat


def load_bool(name, default):
    env_value = os.getenv(name, str(default)).lower()
    return env_value in ("true", "yes", "1", "y", "t")


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "secret-key")
DEBUG = load_bool("DJANGO_DEBUG", False)

MULTI_PART_DATA_FOR_CAMPAIGN = load_bool("MULTI_PART_DATA_CAMPAIGN", False)
USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "core.paginations.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
}

GIGACHAT_MODEL = GigaChat(
    credentials=os.getenv("GIGACHAT_TOKEN"),
    scope=os.getenv("GIGACHAT_SCOPE"),
    model="GigaChat",
    ca_bundle_file=str(BASE_DIR / "../certs/min_cifra_root_ca.cer"),
)

MODERATE_AD_TEXT = load_bool("MODERATE_AD_TEXT", False)

SPECTACULAR_SETTINGS = {
    "TITLE": "Project API",
    "DESCRIPTION": "description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INSTALLED_APPS = [
    "clients",
    "advertisers",
    "core",
    "stats",
    "drf_spectacular",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]


ROOT_URLCONF = "conf.urls"
APPEND_SLASH = False
MEDIA_ROOT = BASE_DIR / "media/"
MEDIA_URL = "/media/"


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

WSGI_APPLICATION = "conf.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": "5432",
    }
}
