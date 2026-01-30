import os
from pathlib import Path

import django.conf.global_settings
import sentry_sdk
from corsheaders.defaults import default_headers
from csp.constants import NONE, SELF
from environ import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber
from sentry_sdk.types import SamplingContext

from pysakoinnin_sahk_asiointi.utils import sentry_scrubber

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(
    # Resilient logger config
    AUDIT_LOG_ENV=(str, ""),
    AUDIT_LOG_ES_URL=(str, ""),
    AUDIT_LOG_ES_INDEX=(str, ""),
    AUDIT_LOG_ES_USERNAME=(str, ""),
    AUDIT_LOG_ES_PASSWORD=(str, ""),
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, "postgres://parking-user:root@localhost:5432/parking-service"),
    DATABASE_PASSWORD=(str, ""),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "local"),
    SENTRY_PROFILE_SESSION_SAMPLE_RATE=(float, None),
    SENTRY_RELEASE=(str, None),
    SENTRY_TRACES_SAMPLE_RATE=(float, None),
    SENTRY_TRACES_IGNORE_PATHS=(list, ["/health", "/readiness"]),
    ATV_API_KEY=(str, ""),
    ATV_ENDPOINT=(str, ""),
    TOKEN_AUTH_AUDIENCE=(list, []),
    TOKEN_AUTH_ISSUER=(list, []),
    TOKEN_AUTH_AUTHORIZATION_FIELD=(list, []),
    TOKEN_AUTH_SCOPE_PREFIX=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGIN_REGEXES=(list, []),
    CLAMAV_HOST=(str, ""),
    GDPR_API_QUERY_SCOPE=(str, "gdprquery"),
    GDPR_API_DELETE_SCOPE=(str, "gdprdelete"),
    HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=(bool, True),
    STATIC_ROOT=(str, str(BASE_DIR / "static/")),
    VALIDATE_PASI_CERTIFICATION=(bool, True),
    PASI_ENDPOINT=(str, ""),
    PASI_AUTH_KEY=(str, ""),
    PASI_API_KEY=(str, ""),
    OUTGOING_REQUEST_TIMEOUT=(int, 30),
    CSP_ENFORCE=(bool, False),
    CSP_REPORT_URI=(str, None),
    STALE_MESSAGE_THRESHOLD_DAYS=(int, 2),
)

env_file_path = str(BASE_DIR / "config.env")
if os.path.exists(env_file_path):
    Env.read_env(env_file_path)

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
    "request",  # WSGIRequest.__str__ may contain query params
    "body",  # request body encoded in JSON in urllib3
    "httplib_request_kw",  # same as "body"
]

SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE")
SENTRY_TRACES_IGNORE_PATHS = env("SENTRY_TRACES_IGNORE_PATHS")


def sentry_traces_sampler(sampling_context: SamplingContext) -> float:
    # Respect parent sampling decision if one exists. Recommended by Sentry.
    if (parent_sampled := sampling_context.get("parent_sampled")) is not None:
        return float(parent_sampled)

    # Exclude health check endpoints from tracing
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO", "")
    if path.rstrip("/") in SENTRY_TRACES_IGNORE_PATHS:
        return 0

    # Use configured sample rate for all other requests
    return SENTRY_TRACES_SAMPLE_RATE or 0


if env("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=env("SENTRY_ENVIRONMENT"),
        release=env("SENTRY_RELEASE"),
        integrations=[DjangoIntegration()],
        traces_sampler=sentry_traces_sampler,
        profile_session_sample_rate=env("SENTRY_PROFILE_SESSION_SAMPLE_RATE"),
        profile_lifecycle="trace",
        event_scrubber=EventScrubber(denylist=sentry_deny_list, recursive=True),
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
    "csp",
    "pysakoinnin_sahk_asiointi",
    "api",
    "mail_service",
    "ninja",
    "corsheaders",
    "anymail",
    "mailer",
    "logger_extra",
    "resilient_logger",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "logger_extra.middleware.XRequestIdMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "api.audit_log.AuditLogMiddleware",
]

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOWED_ORIGIN_REGEXES = env("CORS_ALLOWED_ORIGIN_REGEXES")
CORS_ALLOW_HEADERS = (
    *default_headers,
    "baggage",
    "sentry-trace",
)

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

if env("DATABASE_PASSWORD"):
    DATABASES["default"]["PASSWORD"] = env("DATABASE_PASSWORD")

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
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

# Not required/useful in a container based environment.
MAILER_USE_FILE_LOCK = False

# After how many failed attempts email is not being put back to queue with
# retry_deferred command
MAILER_EMAIL_MAX_RETRIES = 5

EMAIL_HOST = "relay.hel.fi"
EMAIL_PORT = 25
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "pysakoinnin-asiointi-noreply@hel.fi"

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


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["context"],
        },
    },
    "filters": {
        "context": {
            "()": "logger_extra.filter.LoggerContextFilter",
        }
    },
    "formatters": {
        "json": {
            "()": "logger_extra.formatter.JSONFormatter",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Resilient logger settings
RESILIENT_LOGGER = {
    "origin": "pysakoinnin-sahkoinen-asiointi-api",
    "environment": env("AUDIT_LOG_ENV"),
    "sources": [
        {
            "class": "resilient_logger.sources.ResilientLogSource",
        }
    ],
    "targets": [
        {
            "class": "resilient_logger.targets.ElasticsearchLogTarget",
            "es_url": env("AUDIT_LOG_ES_URL"),
            "es_username": env("AUDIT_LOG_ES_USERNAME"),
            "es_password": env("AUDIT_LOG_ES_PASSWORD"),
            "es_index": env("AUDIT_LOG_ES_INDEX"),
            "required": True,
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
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
GDPR_API_QUERY_SCOPE = env("GDPR_API_QUERY_SCOPE")
GDPR_API_DELETE_SCOPE = env("GDPR_API_DELETE_SCOPE")

OUTGOING_REQUEST_TIMEOUT = env("OUTGOING_REQUEST_TIMEOUT")

# Stale message check settings
STALE_MESSAGE_THRESHOLD_DAYS = env("STALE_MESSAGE_THRESHOLD_DAYS")


content_security_policy_configuration = {
    "DIRECTIVES": {
        "default-src": [NONE],
        "connect-src": [SELF],
        "img-src": [SELF, "data:"],
        "form-action": [SELF],
        "frame-ancestors": [SELF],
        "script-src": [
            SELF,
        ],
        "style-src": [
            SELF,
        ],
        "upgrade-insecure-requests": True,
    },
}

if report_uri := env("CSP_REPORT_URI"):
    content_security_policy_configuration["DIRECTIVES"]["report-uri"] = report_uri

if env("CSP_ENFORCE"):
    CONTENT_SECURITY_POLICY = content_security_policy_configuration
    CONTENT_SECURITY_POLICY_REPORT_ONLY = None

else:
    CONTENT_SECURITY_POLICY = None
    CONTENT_SECURITY_POLICY_REPORT_ONLY = content_security_policy_configuration
