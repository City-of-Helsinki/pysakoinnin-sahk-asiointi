from django.contrib import admin

from message_service.models import DeliveryReport, Message

admin.site.register(Message)
admin.site.register(DeliveryReport)
