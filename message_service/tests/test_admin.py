import uuid
from datetime import timedelta

import pytest
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone

from message_service.admin import DeliveryReportAdmin, MessageAdmin
from message_service.enums import DeliveryStatus, MessageType
from message_service.models import DeliveryReport, Message
from pysakoinnin_sahk_asiointi.models import User


@pytest.fixture
def superuser(db):
    return User.objects.create(
        uuid=uuid.uuid4(),
        username="admin-user",
        email="admin.user@example.com",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )


def test_models_registered_with_custom_admins():
    assert isinstance(admin.site._registry[DeliveryReport], DeliveryReportAdmin)
    assert isinstance(admin.site._registry[Message], MessageAdmin)


@pytest.mark.django_db
def test_delivery_report_admin_changelist_default_ordering(client, superuser):
    older = DeliveryReport.objects.create(
        transaction_id="tx-older",
        status=DeliveryStatus.SENT_EMAIL,
        message_type=MessageType.STATUS_RECEIVED,
    )
    newer = DeliveryReport.objects.create(
        transaction_id="tx-newer",
        status=DeliveryStatus.SENT_SUOMIFI,
        message_type=MessageType.DUE_DATE_EXTENDED,
    )
    DeliveryReport.objects.filter(pk=older.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    client.force_login(superuser)
    response = client.get(reverse("admin:message_service_deliveryreport_changelist"))

    assert response.status_code == 200
    result_ids = [obj.pk for obj in response.context["cl"].result_list]
    assert result_ids == [newer.pk, older.pk]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_attr",
    ["transaction_id", "suomifi_id", "external_id"],
)
def test_delivery_report_admin_search(client, superuser, query_attr):
    msg = Message.objects.create(
        transaction_id="tx-match",
        subject="Subject",
        body_text="Body",
        body_html="<p>Body</p>",
        message_type=MessageType.STATUS_RECEIVED,
    )
    matching = DeliveryReport.objects.create(
        transaction_id="tx-match",
        suomifi_id=987654,
        queued_message=msg,
        status=DeliveryStatus.SENT_SUOMIFI,
        message_type=MessageType.STATUS_RECEIVED,
    )
    other = DeliveryReport.objects.create(
        transaction_id="tx-other",
        suomifi_id=123456,
        status=DeliveryStatus.SENT_EMAIL,
        message_type=MessageType.OTHER,
    )

    query_map = {
        "transaction_id": matching.transaction_id,
        "suomifi_id": str(matching.suomifi_id),
        "external_id": str(msg.external_id),
    }

    client.force_login(superuser)
    response = client.get(
        reverse("admin:message_service_deliveryreport_changelist"),
        {"q": query_map[query_attr]},
    )

    assert response.status_code == 200
    result_ids = [obj.pk for obj in response.context["cl"].result_list]
    assert result_ids == [matching.pk]
    assert other.pk not in result_ids


@pytest.mark.django_db
def test_delivery_report_admin_filters(client, superuser):
    matching = DeliveryReport.objects.create(
        transaction_id="tx-failed-due",
        status=DeliveryStatus.FAILED,
        message_type=MessageType.DUE_DATE_EXTENDED,
    )
    DeliveryReport.objects.create(
        transaction_id="tx-sent-other",
        status=DeliveryStatus.SENT_EMAIL,
        message_type=MessageType.OTHER,
    )

    client.force_login(superuser)
    response = client.get(
        reverse("admin:message_service_deliveryreport_changelist"),
        {
            "status__exact": DeliveryStatus.FAILED,
            "message_type__exact": MessageType.DUE_DATE_EXTENDED,
        },
    )

    assert response.status_code == 200
    result_ids = [obj.pk for obj in response.context["cl"].result_list]
    assert result_ids == [matching.pk]


@pytest.mark.django_db
def test_delivery_report_admin_is_read_only(client, superuser):
    report = DeliveryReport.objects.create(
        transaction_id="tx-readonly",
        status=DeliveryStatus.QUEUED,
        message_type=MessageType.OTHER,
    )
    client.force_login(superuser)

    change_response = client.get(
        reverse("admin:message_service_deliveryreport_change", args=[report.pk])
    )
    add_response = client.get(reverse("admin:message_service_deliveryreport_add"))
    delete_response = client.get(
        reverse("admin:message_service_deliveryreport_delete", args=[report.pk])
    )

    assert change_response.status_code == 200
    assert add_response.status_code == 403
    assert delete_response.status_code == 403


@pytest.mark.django_db
def test_message_admin_search_and_filter(client, superuser):
    matching = Message.objects.create(
        transaction_id="tx-msg-1",
        queued=True,
        subject="Matching subject",
        body_text="Body",
        body_html="<p>Body</p>",
        audit_action="extend-due-date",
        message_type=MessageType.DUE_DATE_EXTENDED,
    )
    Message.objects.create(
        transaction_id="tx-msg-2",
        queued=False,
        subject="Other subject",
        body_text="Body",
        body_html="<p>Body</p>",
        audit_action="set-document-status",
        message_type=MessageType.STATUS_RECEIVED,
    )

    client.force_login(superuser)
    response = client.get(
        reverse("admin:message_service_message_changelist"),
        {
            "q": str(matching.external_id),
            "queued__exact": "1",
            "message_type__exact": MessageType.DUE_DATE_EXTENDED,
        },
    )

    assert response.status_code == 200
    result_ids = [obj.pk for obj in response.context["cl"].result_list]
    assert result_ids == [matching.pk]


@pytest.mark.django_db
def test_message_admin_disables_add(client, superuser):
    client.force_login(superuser)

    response = client.get(reverse("admin:message_service_message_add"))

    assert response.status_code == 403
