import logging

from resilient_logger.sources import ResilientLogSource

from api.enums import Operation, Status


def _commit_to_audit_log(request, response):
    ResilientLogSource.create_structured(
        level=logging.NOTSET,
        message=_get_status(response),
        actor={"name": "user_id", "value": _get_user_id(request)},
        operation=_get_operation_name(request),
        target={"value": _get_target_uri(request)},
    )


def _get_target_uri(request):
    return request.path


def _get_user_id(request):
    if hasattr(request.user, "uuid"):
        return str(request.user.uuid)
    else:
        return None


def _get_operation_name(request):
    if request.method == "GET":
        return Operation.READ.value
    elif request.method == "POST":
        return Operation.CREATE.value
    elif request.method in ("PUT", "PATCH"):
        return Operation.UPDATE.value
    elif request.method == "DELETE":
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
