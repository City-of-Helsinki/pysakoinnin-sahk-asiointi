from ninja import ModelSchema

from message_service.models import DeliveryReport


class DeliveryReportSchema(ModelSchema):
    class Meta:
        model = DeliveryReport
        fields = [
            "transaction_id",
            "suomifi_id",
            "created_at",
            "updated_at",
            "sent_at",
            "read_at",
            "status",
            "message_type",
        ]
