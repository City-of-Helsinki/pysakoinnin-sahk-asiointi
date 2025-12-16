import logging
from datetime import datetime, timezone

from resilient_logger.sources import ResilientLogSource


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"


def _commit_to_audit_log(mail_to, action):
    """Email message audit log entry creation."""
    ResilientLogSource.create_structured(
        level=logging.NOTSET,
        message=action,
        actor={"name": "SYSTEM", "value": ""},
        operation="SEND_MAIL",
        target={"value": mail_to},
    )
