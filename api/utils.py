import requests
from django.conf import settings
from ninja.errors import HttpError


def virus_scan_attachment_file(file_data):
    try:
        req = requests.request('POST', f"{settings.CLAMAV_HOST}", files={file_data})
        res = req.json()
        if hasattr(res, 'data') and res['data']['is_infected'] is False:
            return
        else:
            return HttpError(400, message="Request failed")
    except Exception as error:
        return error
