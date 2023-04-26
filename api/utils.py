import base64

import requests
from django.conf import settings
from ninja.errors import HttpError


def virus_scan_attachment_file(file_data):
    try:
        req = requests.request('POST', f"{settings.CLAMAV_HOST}", files={'FILES': base64.b64decode(file_data)})
        response = req.json()
        if hasattr(response, 'data') and response['data']['result'][0]['is_infected'] is True:
            raise HttpError(422, message="File is infected")
        return req.json()
    except HttpError as error:
        return error
