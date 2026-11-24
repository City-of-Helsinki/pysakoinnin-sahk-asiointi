import uuid

import pytest
from django.contrib import admin
from django.urls import reverse

from pysakoinnin_sahk_asiointi.models import User


@pytest.fixture
def superuser():
    return User.objects.create(
        uuid=uuid.uuid4(),
        username="admin-user",
        email="admin.user@example.com",
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def regular_user():
    return User.objects.create(
        uuid=uuid.uuid4(),
        username="regular-user",
        email="regular.user@example.com",
        first_name="Regular",
        last_name="User",
        is_active=True,
        is_staff=False,
    )


def test_user_model_is_registered_in_admin():
    assert admin.site.is_registered(User)


@pytest.mark.django_db
def test_user_admin_changelist_accessible_by_superuser(client, superuser, regular_user):
    client.force_login(superuser)

    response = client.get(reverse("admin:pysakoinnin_sahk_asiointi_user_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert superuser.email in content
    assert regular_user.email in content


@pytest.mark.django_db
def test_user_admin_search_by_uuid(client, superuser, regular_user):
    client.force_login(superuser)

    response = client.get(
        reverse("admin:pysakoinnin_sahk_asiointi_user_changelist"),
        {"q": str(regular_user.uuid)},
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert regular_user.email in content
    assert superuser.email not in content


@pytest.mark.django_db
def test_user_admin_change_page_renders_helusers_fields(
    client, superuser, regular_user
):
    client.force_login(superuser)

    response = client.get(
        reverse("admin:pysakoinnin_sahk_asiointi_user_change", args=[regular_user.pk])
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert str(regular_user.uuid) in content
    assert "ad_groups" in content
