from ninja import ModelSchema

from message_service.enums import DeliveryStatus, MessageType
from message_service.models import DeliveryReport


class DeliveryReportSchema(ModelSchema):
    status: DeliveryStatus
    message_type: MessageType

    class Meta:
        model = DeliveryReport
        fields = [
            "id",
            "transaction_id",
            "suomifi_id",
            "created_at",
            "updated_at",
            "sent_at",
            "read_at",
            "status",
            "message_type",
        ]
