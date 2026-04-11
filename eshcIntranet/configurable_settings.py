# Wraps what used to be set per server in local_settings.py to using envars.
import os
from dotenv import load_dotenv

# .env should only really be used for dev
load_dotenv()


def require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def getboolenv(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes")


DEBUG = getboolenv("DEBUG", False)
SECRET_KEY = require_env("SECRET_KEY")

## Database
DATABASES = {
    "default": {
        "ENGINE": require_env("DB_ENGINE"),
        "NAME": os.getenv("DB_NAME", "intranet"),
        "USER": os.getenv("DB_USER", "intranet"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

## Email Authentication
# "django.core.mail.backends.console.EmailBackend" for just stdio
# If on console output, can ignore rest of settings
# "django.core.mail.backends.smtp.EmailBackend" for smtp
EMAIL_BACKEND = require_env("EMAIL_BACKEND")
EMAIL_USE_TLS = getboolenv("EMAIL_USE_TLS", True)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))

## Email Configuration
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_DEFAULT_FROM", "intranet@eshc.coop")
# Email used to send error messages to the below admins
SERVER_EMAIL = os.getenv("EMAIL_SERVER_EMAIL", DEFAULT_FROM_EMAIL)
ADMINS = [("Root", os.getenv("EMAIL_FOR_ERROR_NOTIFICATION"))]


## AWS S3
# AFAIK, unused / not working, keeping anyway
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

## LDAP
LDAP_SERVER_ADDR = os.getenv("LDAP_SERVER_ADDR")
LDAP_SERVER_ROOT_DN = os.getenv("LDAP_SERVER_ROOT_DN")
LDAP_SERVER_AUTH_USER = os.getenv("LDAP_SERVER_AUTH_USER")
LDAP_SERVER_AUTH_PASSWORD = os.getenv("LDAP_SERVER_AUTH_PASSWORD")

## Quickbooks
# AFAIK, not working, keeping anyway
QBO_CLIENT_ID = os.getenv("QBO_CLIENT_ID")
QBO_CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
QBO_ENVIRONMENT = os.getenv("QBO_ENVIRONMENT", "production")
