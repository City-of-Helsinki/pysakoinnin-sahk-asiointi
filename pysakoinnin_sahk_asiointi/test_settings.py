from .settings import *  # noqa

SECRET_KEY = "test"
VALIDATE_PASI_CERTIFICATION = False
TOKEN_AUTH_AUTHORIZATION_FIELD = [
    "https://api.hel.fi/auth",
    "authorization.permissions.scopes",
]
TOKEN_AUTH_SCOPE_PREFIX = [
    "pysakoinninsahkasiointiapidev",
    "access",
    "gdprquery",
    "gdprdelete",
]
TOKEN_AUTH_ISSUER = [
    "https://tunnistamo.test.hel.ninja/openid",
    "https://tunnistus.test.hel.ninja/auth/realms/helsinki-tunnistus",
]
TOKEN_AUTH_AUDIENCE = [
    "https://api.hel.fi/auth/pysakoinninsahkasiointiapidev",
    "pysakoinnin-sahk-asiointi-api-dev",
]
GDPR_API_QUERY_SCOPE = "gdprquery"
GDPR_API_DELETE_SCOPE = "gdprdelete"

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": TOKEN_AUTH_AUDIENCE,
    "ISSUER": TOKEN_AUTH_ISSUER,
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": True,
    "API_AUTHORIZATION_FIELD": TOKEN_AUTH_AUTHORIZATION_FIELD,
    "API_SCOPE_PREFIX": TOKEN_AUTH_SCOPE_PREFIX,
    "OIDC_CONFIG_EXPIRATION_TIME": 600,
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
MAILER_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
