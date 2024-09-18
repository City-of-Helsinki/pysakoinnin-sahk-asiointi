from pathlib import Path
from sys import stdout

import django.conf.global_settings
import sentry_sdk
from corsheaders.defaults import default_headers
from environ import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import EventScrubber, DEFAULT_DENYLIST

from pysakoinnin_sahk_asiointi.utils import sentry_scrubber

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, "postgres://parking-user:root@localhost:5432/parking-service"),
    SENTRY_DSN=(str, ""),
    SENTRY_TRACE_SAMPLE_RATE=(float, 0.0),
    ATV_API_KEY=(str, ""),
    ATV_ENDPOINT=(str, ""),
    TOKEN_AUTH_AUDIENCE=(str, ""),
    TOKEN_AUTH_ISSUER=(str, ""),
    TOKEN_AUTH_AUTHORIZATION_FIELD=(str, ""),
    TOKEN_AUTH_SCOPE_PREFIX=(str, ""),
    CORS_ALLOWED_ORIGINS=(list, []),
    CLAMAV_HOST=(str, ""),
    GDPR_API_AUDIENCE=(str, ""),
    GDPR_API_ISSUER=(str, ""),
    GDPR_API_QUERY_SCOPE=(str, "gdprquery"),
    GDPR_API_DELETE_SCOPE=(str, "gdprdelete"),
    HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=(bool, True),
    STATIC_ROOT=(str, str(BASE_DIR / "static/")),
    VALIDATE_PASI_CERTIFICATION=(bool, True),
    PASI_ENDPOINT=(str, ""),
    PASI_AUTH_KEY=(str, ""),
    PASI_API_KEY=(str, ""),
)

Env.read_env(str(BASE_DIR / "config.env"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SECRET_KEY = env("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    SECRET_KEY = "XXX"

# Sentry config
sentry_deny_list = DEFAULT_DENYLIST + [
    "ssn",
    "address",
    "firstName",
    "first_name",
    "lastName",
    "last_name",
    "mobilePhone",
    "mobile_phone",
    "email",
    "registerNumber",
    "register_number",
]

sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    event_scrubber=EventScrubber(denylist=sentry_deny_list),
    traces_sample_rate=env("SENTRY_TRACE_SAMPLE_RATE"),
    before_send=sentry_scrubber,
)

# Application definition

INSTALLED_APPS = [
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pysakoinnin_sahk_asiointi",
    "api",
    "mail_service",
    "ninja",
    "corsheaders",
    "anymail",
    "mailer",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.audit_log.AuditLogMiddleware",
]

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_HEADERS = list(default_headers) + ["baggage", "sentry-trace"]

ROOT_URLCONF = "pysakoinnin_sahk_asiointi.urls"

AUTH_USER_MODEL = "pysakoinnin_sahk_asiointi.User"

HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED = env("HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED")

OIDC_API_TOKEN_AUTH = {
    # Audience that must be present in the token for it to be
    # accepted. Value must be agreed between your SSO service and your
    # application instance. Essentially this allows your application to
    # know that the token is meant to be used with it.
    # RequestJWTAuthentication supports multiple acceptable audiences,
    # so this setting can also be a list of strings.
    # This setting is required.
    "AUDIENCE": env("TOKEN_AUTH_AUDIENCE"),
    # Who we trust to sign the tokens. The library will request the
    # public signature keys from standard locations below this URL.
    # RequestJWTAuthentication supports multiple issuers, so this
    # setting can also be a list of strings.
    "ISSUER": env("TOKEN_AUTH_ISSUER"),
    # The following can be used if you need certain scopes for any
    # functionality of the API. Usually this is not needed, as checking
    # the audience is enough. Default is False.
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": True,
    # The name of the claim that is used to read in the scopes from the JWT.
    "API_AUTHORIZATION_FIELD": env("TOKEN_AUTH_AUTHORIZATION_FIELD"),
    # The request will be denied if scopes don't contain anything starting
    # with the value provided here.
    "API_SCOPE_PREFIX": env("TOKEN_AUTH_SCOPE_PREFIX"),
    # In order to do the authentication RequestJWTAuthentication needs
    # some facts from the authorization server, mainly its public keys for
    # verifying the JWT's signature. This setting controls the time how long
    # authorization server configuration and public keys are "remembered".
    # The value is in seconds. Default is 24 hours.
    "OIDC_CONFIG_EXPIRATION_TIME": 600,
}

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

WSGI_APPLICATION = "pysakoinnin_sahk_asiointi.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {"default": env.db()}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Default backend which is responsible for putting emails so to queue
EMAIL_BACKEND = "mailer.backend.DbBackend"

# Actual backend responsible for sending emails
# Sometimes this is referred in code directly to skip queue
MAILER_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

MAILER_ERROR_HANDLER = "mail_service.utils.custom_mailer_error_handler"

# After how many failed attempts email is not being put back to queue with retry_deferred command
MAILER_EMAIL_MAX_RETRIES = 5

EMAIL_HOST = "relay.hel.fi"
EMAIL_PORT = 25
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "noreply@hel.fi"

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = env("STATIC_ROOT")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_audit_log_handler = {
    "level": "INFO",
    "class": "logging.StreamHandler",
    "stream": stdout,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"audit": _audit_log_handler},
    "loggers": {"audit": {"handlers": ["audit"], "level": "ERROR", "propagate": True}},
}

# Malware protection
CLAMAV_HOST = env("CLAMAV_HOST")

# Increase max data upload size to accommodate common use cases
django.conf.global_settings.DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520

VALIDATE_PASI_CERTIFICATION = env("VALIDATE_PASI_CERTIFICATION")
PASI_ENDPOINT = env("PASI_ENDPOINT")
PASI_AUTH_KEY = env("PASI_AUTH_KEY")
PASI_API_KEY = env("PASI_API_KEY")
ATV_ENDPOINT = env("ATV_ENDPOINT")
ATV_API_KEY = env("ATV_API_KEY")

# GDPR settings
GDPR_API_AUDIENCE = env("GDPR_API_AUDIENCE")
GDPR_API_ISSUER = env("GDPR_API_ISSUER")
GDPR_API_QUERY_SCOPE = env("GDPR_API_QUERY_SCOPE")
GDPR_API_DELETE_SCOPE = env("GDPR_API_DELETE_SCOPE")
