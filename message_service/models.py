import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from message_service import utils


class Message(models.Model):
    delivery_report: "DeliveryReport"
    transaction_id = models.CharField()
    # delivery_report = models.OneToOneField(DeliveryReport, on_delete=models.PROTECT)

    queued = models.BooleanField()
    subject = models.TextField()

    body_text = models.TextField()
    body_html = models.TextField()

    send_attempt_count = models.IntegerField(default=0)

    external_id = models.UUIDField(default=uuid.uuid4)

    def get_or_create_delivery_report(self):
        try:
            return self.delivery_report
        except DeliveryReport.DoesNotExist:
            return DeliveryReport.objects.create(
                transaction_id=self.transaction_id, queued_message=self
            )

    def send(self):
        try:
            utils.send_message(self)
            self.delete()
        except:  # TODO
            if not self.queued:
                self.queued = True
                self.save()


class DeliveryReport(models.Model):
    class DeliveryStatus(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT_SUOMIFI = "sent_suomifi", _("Sent via Suomi.fi messages")
        SENT_EMAIL = "sent_email", _("Sent via e-mail")
        FAILED = "failed", _("Failed")

    queued_message = models.ForeignKey(Message, null=True, on_delete=models.SET_NULL)

    transaction_id = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.TextField(choices=DeliveryStatus, default=DeliveryStatus.QUEUED)

    sent_at = models.DateTimeField(null=True)
    read_at = models.DateTimeField(null=True)

    suomfi_id = models.IntegerField(null=True)


class SuomifiPersistence(models.Model):
    continuation_token = models.TextField()


# class SuomifiEvent(models.Model):
#     delivery_report = models.ForeignKey(DeliveryReport, on_delete=models.CASCADE)
#     event_time = models.DateTimeField()
#     event_type = models.TextField()


# class DeliveryError(models.Model):
#     delivery_report = models.ForeignKey(DeliveryReport, on_delete=models.CASCADE)
#     error_message = models.TextField()
