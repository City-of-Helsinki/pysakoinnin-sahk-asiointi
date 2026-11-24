import uuid

import pytest
from django.contrib.auth import SESSION_KEY
from django.urls import reverse

from pysakoinnin_sahk_asiointi.models import User

TEST_PASSWORD = "test-admin-password"


@pytest.fixture
def staff_user():
    user = User.objects.create(
        uuid=uuid.uuid4(),
        username="staff-user",
        email="staff.user@example.com",
        is_active=True,
        is_staff=True,
    )
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.mark.django_db
def test_admin_login_offers_central_helsinki_login(client):
    response = client.get(reverse("admin:login"))

    assert response.status_code == 200
    assert reverse("helusers:auth_login") in response.content.decode()


@pytest.mark.django_db
def test_central_login_redirects_to_oidc_preserving_next(client):
    next_url = reverse("admin:index")

    response = client.post(reverse("helusers:auth_login"), {"next": next_url})

    assert response.status_code == 307
    assert response["Location"] == reverse(
        "social:begin",
        kwargs={"backend": "tunnistamo"},
        query={"next": next_url},
    )


@pytest.mark.django_db
@pytest.mark.parametrize("disabled", [False, True])
def test_password_login_respects_setting(client, settings, staff_user, disabled):
    settings.HELUSERS_PASSWORD_LOGIN_ALLOWLIST = []
    settings.HELUSERS_PASSWORD_LOGIN_DISABLED = disabled

    logged_in = client.login(username=staff_user.username, password=TEST_PASSWORD)

    assert logged_in is (not disabled)


@pytest.mark.django_db
def test_active_staff_user_can_access_admin(client, staff_user):
    client.force_login(staff_user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_non_staff_user_cannot_access_admin(client, staff_user):
    staff_user.is_staff = False
    staff_user.save()
    client.force_login(staff_user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 302
    assert (
        response["Location"]
        == f"{reverse('admin:login')}?next={reverse('admin:index')}"
    )


@pytest.mark.django_db
def test_logout_clears_authenticated_session(client, staff_user):
    client.force_login(staff_user)
    assert SESSION_KEY in client.session

    response = client.post(reverse("helusers:auth_logout"))

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:index")
    assert SESSION_KEY not in client.session


def test_forwarded_proto_header_marks_request_secure(rf):
    request = rf.get(reverse("admin:login"), HTTP_X_FORWARDED_PROTO="https")

    assert request.is_secure() is True
    assert request.build_absolute_uri(reverse("admin:login")).startswith("https://")
