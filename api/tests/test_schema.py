import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_schema_matches_the_reference(client, snapshot):
    response = client.get(reverse("ninja:openapi-json"))

    snapshot.assert_match(response.json())
