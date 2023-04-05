from django.conf import settings
from ninja.errors import HttpError
from pyclamd import pyclamd


def virus_scan_attachment_file(file_data):
    cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST)
    if cd.scan_stream(file_data) is not None:
        raise HttpError(400, message="Malicious file detected")
