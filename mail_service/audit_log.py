from datetime import datetime, timezone

from api.models import AuditLog

ORIGIN = "PARKING_E-SERVICE"


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"


def _commit_to_audit_log(mail_to, action):
    """
    Write an event to the audit log.
    Each audit log event has an actor (or None for system events),
    an operation(e.g. READ or UPDATE), the target of the operation
    (a Django model instance), status (e.g. SUCCESS), and a timestamp.
    Audit log events are written to the "audit" logger at "INFO" level.
    """
    current_time = _now()
    message = {"audit_event": {
        "origin": ORIGIN,
        "action": action,
        "date_time_epoch": int(current_time.timestamp() * 1000),
        "date_time": _iso8601_date(current_time),
        "actor": {
            "profile_id": None,
        },
        "operation": 'send_mail',
        "target": mail_to
    }, }

    AuditLog.objects.create(message=message)
