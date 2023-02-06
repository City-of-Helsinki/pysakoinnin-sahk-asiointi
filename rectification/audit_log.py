from datetime import datetime, timezone
from typing import Optional

from django.db.models import Model

from rectification.enums import Operation
from rectification.models import AuditLog

ORIGIN = "PARKING_E-SERVICE"


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"


def _commit_to_audit_log(request
                         ):
    """
    Write an event to the audit log.
    Each audit log event has an actor (or None for system events),
    an operation(e.g. READ or UPDATE), the target of the operation
    (a Django model instance), status (e.g. SUCCESS), and a timestamp.
    Audit log events are written to the "audit" logger at "INFO" level.
    """
    current_time = _now()
    profile_id = None
    message = {
        "audit_event": {
            "origin": ORIGIN,
            "status": "TEST",
            "date_time_epoch": int(current_time.timestamp() * 1000),
            "date_time": _iso8601_date(current_time),
            "actor": {
                "role": "ANONYMOUS",
                "profile_id": profile_id,
            },
            "operation": _get_operation_name(request),
            "target": {
                "id": "TEST",
                "type": None
            },
        },
    }
    AuditLog.objects.create(message=message)


def _get_target_id(instance: Optional[Model]) -> Optional[str]:
    if instance is None or instance.pk is None:
        return None
    field_name = getattr(instance, "audit_log_id_field", "pk")
    audit_log_id = getattr(instance, field_name, None)
    return str(audit_log_id)


def _get_operation_name(request):
    if request.method == 'GET':
        return Operation.READ.value
    elif request.method == 'POST':
        return Operation.CREATE.value
    elif request.method == 'PUT' | 'PATCH':
        return Operation.UPDATE.value
    elif request.method == 'DELETE':
        return Operation.DELETE.value


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        _commit_to_audit_log(request)

        return response
