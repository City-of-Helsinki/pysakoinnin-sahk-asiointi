from datetime import datetime, timezone

from api.enums import Operation, Status
from api.models import AuditLog

ORIGIN = "PARKING_E-SERVICE"


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(sep='T', timespec='milliseconds')}Z"


def _commit_to_audit_log(request, response
                         ):
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
        "status": _get_status(response),
        "date_time_epoch": int(current_time.timestamp() * 1000),
        "date_time": _iso8601_date(current_time),
        "actor": {
            "profile_id": _get_profile_id(request),
        },
        "operation": _get_operation_name(request),
        "target": _get_target_uri(request)
    }, }

    AuditLog.objects.create(message=message)


def _get_target_uri(request):
    return request.path

  
def _get_profile_id(request):
    if hasattr(request.user, "uuid"):
        return str(request.user.uuid)
    else:
        return None


def _get_operation_name(request):
    if request.method == 'GET':
        return Operation.READ.value
    elif request.method == 'POST':
        return Operation.CREATE.value
    elif request.method == 'PUT' or 'PATCH':
        return Operation.UPDATE.value
    elif request.method == 'DELETE':
        return Operation.DELETE.value


def _get_status(response):
    if response.status_code == 200 or response.status_code == 201:
        return Status.SUCCESS.value
    elif response.status_code == 401 or response.status_code == 403:
        return Status.FORBIDDEN.value
    else:
        return Status.FAILED.value


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if "health" in request.path or "readiness" in request.path:
            pass
        else:
            _commit_to_audit_log(request, response)

        return response
