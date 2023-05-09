from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    id = models.IntegerField
    is_sent = models.BooleanField(default=False)
    message = JSONField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    def __str__(self):
        return " ".join(
            [
                _safe_get(self.message.audit_event, "origin"),
                _safe_get(self.message.audit_event, "status"),
                _safe_get(self.message.audit_event, "date_time"),
                _safe_get(self.message.audit_event, "date_time_epoch"),
                _safe_get(self.message.audit_event, "actor", "profile_id"),
                _safe_get(self.message.audit_event, "operation"),
                _safe_get(self.message.audit_event, "target")
            ]
        )


def _safe_get(value: dict, *keys: str) -> str:
    """Look up a nested key in the given dict, or return "UNKNOWN" on KeyError."""
    for key in keys:
        try:
            value = value[key]
        except KeyError:
            return "UNKNOWN"
    return str(value)
