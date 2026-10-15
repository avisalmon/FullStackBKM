"""
Django settings - environment-driven and production-ready for Render.

One file, no settings_local.py: everything that differs between your laptop and
production is an environment variable. Locally they come from `.env` (copy
`.env.example`); on Render they come from render.yaml / the dashboard.
See docs/procedures/env_vars.md for the full list.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# No-op when .env is absent (e.g. on Render, where real env vars are set).
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------
DEV_SECRET_KEY = "dev-only-insecure-key"
SECRET_KEY = os.environ.get("SECRET_KEY") or DEV_SECRET_KEY  # an empty value counts as unset
DEBUG = env_bool("DEBUG", True)

# Fail closed: production must never boot on the well-known development key.
if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set when DEBUG is False.")

SITE_NAME = os.environ.get("SITE_NAME", "My Site")

# Render injects RENDER_EXTERNAL_HOSTNAME (e.g. my-site-ab12.onrender.com) into every
# web service. Trusting it automatically removes the "400 Bad Request after first
# deploy because ALLOWED_HOSTS has the wrong hostname" trap. Custom domains are added
# through the ALLOWED_HOSTS env var (docs/procedures/custom_domain_dns.md).
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
_LOCAL_HOSTS = ["127.0.0.1", "localhost", "testserver"]

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ",".join(_LOCAL_HOSTS))
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

# CSRF origins are derived from ALLOWED_HOSTS (https for every real host), so a custom
# domain is added in exactly one place. CSRF_TRUSTED_ORIGINS adds extras if needed.
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in _LOCAL_HOSTS and "*" not in host
]
CSRF_TRUSTED_ORIGINS += [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
CSRF_TRUSTED_ORIGINS += env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    # Site-level pages (home, health check, robots). Keep it small.
    "core",
    # Example app that demonstrates docs/building_an_app.md. Delete it (and its URL
    # include + docs/notes/) once you have copied the pattern for your own app.
    "notes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # must sit directly after Security
    "core.middleware.PermissionsPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "mysite.urls"

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
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# --------------------------------------------------------------------------
# Persistent storage
# --------------------------------------------------------------------------
# On Render the persistent disk is mounted at /var/data and is NOT writable during the
# build phase. Locally PERSISTENT_ROOT falls back to the repo (data/ and media/ are
# git-ignored).
PERSISTENT_ROOT = Path(os.environ.get("PERSISTENT_ROOT", BASE_DIR))
DATA_DIR = PERSISTENT_ROOT / "data"
MEDIA_DIR = PERSISTENT_ROOT / "media"
BACKUP_DIR = PERSISTENT_ROOT / "backups"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass  # Disk not mounted yet (build phase). The directories are created at runtime.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db.sqlite3"),
        "OPTIONS": {
            # WAL lets readers proceed during a write; IMMEDIATE avoids the
            # "database is locked" upgrade deadlock under concurrent writers.
            "init_command": (
                "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA busy_timeout=5000;"
            ),
            "transaction_mode": "IMMEDIATE",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static and media files
# --------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Prod: hashed + compressed (long cache, cache-busting via manifest).
        # Dev: plain storage so edits to static/ show up live with no collectstatic.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = MEDIA_DIR

# --------------------------------------------------------------------------
# HTTPS / security (all gated on DEBUG so local development stays plain http)
# --------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
# The health check must answer 200 directly, never a 301 to https.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
# Cookie hygiene. HttpOnly keeps scripts from reading the session; SameSite=Lax stops other sites
# from riding your visitors' sessions; a two-week session is a privacy default (shared computers).
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = int(os.environ.get("SESSION_COOKIE_AGE", str(14 * 24 * 3600)))
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = (
    "same-origin"  # don't tell other sites which of your pages sent the visitor
)
X_FRAME_OPTIONS = "DENY"
# Browser features the site may use. Empty parentheses = none. See core/middleware.py.
PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
# Flip to True (env var) once YOU have read /privacy/ and /terms/ and are happy with them: the
# "draft" banner on those pages disappears. Until then verify_site.py reminds you.
PRIVACY_REVIEWED = env_bool("PRIVACY_REVIEWED", False)

# --------------------------------------------------------------------------
# Auth: django-allauth (email login, optional Google OAuth)
# --------------------------------------------------------------------------
SITE_ID = 1
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
# Templates only show "Continue with Google" when both values are set.
GOOGLE_LOGIN_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {"client_id": GOOGLE_CLIENT_ID, "secret": GOOGLE_CLIENT_SECRET},
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}
SOCIALACCOUNT_LOGIN_ON_GET = True  # skip the "Continue with Google?" interstitial
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# allauth 65.x settings. The old ACCOUNT_EMAIL_REQUIRED / ACCOUNT_AUTHENTICATION_METHOD
# are deprecated and warn on every command.
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
# Do not mail addresses we have no account for. allauth's enumeration guard otherwise
# answers every login/reset attempt with an "unknown account" email, so a bot posting
# random addresses makes you mail strangers on demand (it burned a whole Resend daily
# quota on the reference site).
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False

# --------------------------------------------------------------------------
# Email: Resend via django-anymail when RESEND_API_KEY is set, console otherwise
# --------------------------------------------------------------------------
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
if RESEND_API_KEY:
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {"RESEND_API_KEY": RESEND_API_KEY, "REQUESTS_TIMEOUT": 30}
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Where error alerts go (Django mails ADMINS on every unhandled 500, when email works).
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "").strip()
ADMINS = [("Owner", OWNER_EMAIL)] if OWNER_EMAIL else []
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# --------------------------------------------------------------------------
# OpenAI (core/ai.py): empty key = stub mode, the site works and spends nothing
# --------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_DEFAULT_MODEL = os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
OPENAI_MONTHLY_COST_CAP_USD = float(os.environ.get("OPENAI_MONTHLY_COST_CAP_USD", "20"))  # 0 = off
OPENAI_DAILY_TOKEN_LIMIT_PER_USER = int(
    os.environ.get("OPENAI_DAILY_TOKEN_LIMIT_PER_USER", "50000")
)

# --------------------------------------------------------------------------
# Costs, backups, scheduled tasks, analytics
# --------------------------------------------------------------------------
MONTHLY_BUDGET_USD = float(os.environ.get("MONTHLY_BUDGET_USD", "0"))  # 0 = no alerts
RENDER_MONTHLY_USD = float(os.environ.get("RENDER_MONTHLY_USD", "7.25"))  # Starter + 1 GB disk
DOMAIN_YEARLY_USD = float(os.environ.get("DOMAIN_YEARLY_USD", "0"))
# Shared secret for POST /internal/run/<task>/ (GitHub Actions cron). Unset = endpoint closed.
TASK_TRIGGER_TOKEN = os.environ.get("TASK_TRIGGER_TOKEN", "")
PLAUSIBLE_DOMAIN = os.environ.get("PLAUSIBLE_DOMAIN", "")

# --------------------------------------------------------------------------
# Django REST Framework (docs/building_an_app.md, Rule 6: every app has a CRUD API)
# --------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    # Deny by default; a viewset that wants to be public must say so explicitly.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# --------------------------------------------------------------------------
# Logging: everything to stdout, which is what Render's log stream captures
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "{asctime} {levelname} {name} {message}", "style": "{"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        # Mails OWNER_EMAIL on unhandled errors in production; a no-op while ADMINS is empty.
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "mail_admins"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
