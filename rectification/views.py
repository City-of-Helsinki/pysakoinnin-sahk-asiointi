import json

from environ import Env
from requests import request

env = Env()


class ATVHandler:
    def get_documents(self):
        try:
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?user_id=35513524-486D-4C0D-AE80-E263DBAEE4DC",
                          headers={"x-api-key": env('ATV_API_KEY')})
            return req.json()
        except Exception as error:
            return str(error)

    def add_document(self):
        try:
            req = request('POST', f"{env('ATV_ENDPOINT')}",
                          headers={"x-api-key": env('ATV_API_KEY')}, data={
                    "draft": False,
                    "tos_record_id": 12345,
                    "tos_function_id": 12345,
                    "content": json.dumps({
                        "title": "Just testing",
                        "body": "Written text in json object"
                    }),
                    "user_id": "35513524-486D-4C0D-AE80-E263DBAEE4DC"
                },
                          files={'attachments': None})
            return req.json()
        except Exception as error:
            return str(error)
