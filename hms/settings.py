"""Django settings for the Hospital Management System (HMS).

Database is MySQL by default. Configure it with environment variables:
    DB_ENGINE=mysql | sqlite | postgres   (default: postgres if DATABASE_URL is set, else mysql)
    DATABASE_URL                          (for postgres, e.g. Neon on Vercel)
    DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-change-me-in-production-hms-2026"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Running on Vercel (serverless): read-only filesystem, HTTPS, *.vercel.app domain
ON_VERCEL = bool(os.environ.get("VERCEL"))
if ON_VERCEL:
    ALLOWED_HOSTS += [".vercel.app"]
    CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
    # Sessions live in signed cookies so logins work across serverless instances
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    # HMS apps
    "core",
    "accounts",
    "patients",
    "doctors",
    "departments",
    "appointments",
    "consultations",
    "admissions",
    "laboratory",
    "pharmacy",
    "billing",
    "payments",
    "staff",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "hms.wsgi.application"

# ---------------------------------------------------------------- Database
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_ENGINE = os.environ.get(
    "DB_ENGINE", "postgres" if DATABASE_URL else "sqlite" if ON_VERCEL else "mysql"
).lower()

if DB_ENGINE == "postgres":
    # Hosted Postgres (Neon on Vercel). DATABASE_URL looks like
    # postgres://user:password@host/dbname?sslmode=require
    from urllib.parse import parse_qsl, unquote, urlparse
    _u = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _u.path.lstrip("/"),
            "USER": unquote(_u.username or ""),
            "PASSWORD": unquote(_u.password or ""),
            "HOST": _u.hostname,
            "PORT": _u.port or 5432,
            "OPTIONS": {"sslmode": dict(parse_qsl(_u.query)).get("sslmode", "require")},
            "CONN_MAX_AGE": 0,
            # Neon's pooled URL goes through PgBouncer (transaction mode)
            "DISABLE_SERVER_SIDE_CURSORS": True,
        }
    }
elif DB_ENGINE == "sqlite":
    SQLITE_PATH = BASE_DIR / "db.sqlite3"
    if ON_VERCEL:
        # The deployment bundle is read-only: work on a copy in /tmp.
        # Changes last only as long as the serverless instance (demo use).
        import shutil
        tmp_db = Path("/tmp/db.sqlite3")
        if not tmp_db.exists():
            shutil.copyfile(SQLITE_PATH, tmp_db)
        SQLITE_PATH = tmp_db
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": SQLITE_PATH,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "hospital_db"),
            "USER": os.environ.get("DB_USER", "root"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

if "test" in sys.argv:  # fast hashing so the test suite runs quickly
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Africa/Nairobi")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# WhiteNoise serves static files straight from the app/static folders (no collectstatic needed)
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": ["rest_framework.filters.SearchFilter",
                                "rest_framework.filters.OrderingFilter"],
}

CURRENCY = os.environ.get("HMS_CURRENCY", "UGX")
