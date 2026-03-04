from django.contrib import admin

from message_service.models import DeliveryReport, QueuedMessage

admin.site.register(QueuedMessage)
admin.site.register(DeliveryReport)
