import base64

import requests
from django.conf import settings
from ninja.errors import HttpError


def virus_scan_attachment_file(file_data):
    try:
        response = requests.post(
            settings.CLAMAV_HOST,
            files={"FILES": base64.b64decode(file_data + "==")},
            timeout=settings.OUTGOING_REQUEST_TIMEOUT,
        )
        response_json = response.json()
        if (
            hasattr(response_json, "data")
            and response_json["data"]["result"][0]["is_infected"] is True
        ):
            raise HttpError(422, message="File is infected")
        return response_json
    except HttpError as error:
        return error
