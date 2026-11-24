from django.contrib import admin

from message_service.models import DeliveryReport, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "message_type",
        "queued",
        "send_failure_count",
        "created_at",
        "external_id",
        "audit_action",
    )
    list_filter = (
        "queued",
        "message_type",
        "created_at",
    )
    search_fields = (
        "transaction_id",
        "external_id",
        "audit_action",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "external_id",
    )

    def has_add_permission(self, request):
        return False


@admin.register(DeliveryReport)
class DeliveryReportAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "status",
        "message_type",
        "suomifi_id",
        "created_at",
        "sent_at",
        "read_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "message_type",
        "created_at",
    )
    search_fields = (
        "transaction_id",
        "suomifi_id",
        "queued_message__external_id",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
