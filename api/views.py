import json

from environ import Env
from requests import request

env = Env()


class ATVHandler:
    @staticmethod
    def get_documents():
        try:
            req = request("GET", url=f"{env('ATV_ENDPOINT')}?user_id=35513524-486D-4C0D-AE80-E263DBAEE4DC",
                          headers={"x-api-key": env('ATV_API_KEY')})
            return req
        except Exception as error:
            return str(error)

    @staticmethod
    def add_document():
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
            return req
        except Exception as error:
            return str(error)


class PASIHandler:

    @staticmethod
    def get_foul_data(foul_number, register_number):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/GetFoulData",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={
                              "username": "string",
                              "password": "string",
                              "customerID": {
                                  "id": "string",
                                  "type": 0
                              },
                              "customerLanguage": 0,
                              "customerIPAddress": "string",
                              "foulNumber": foul_number,
                              "registerNumber": f"{register_number}"
                          })
            return req
        except Exception as error:
            return {"status_code": 500, "error": error}

    @staticmethod
    def extend_foul_due_date(foul_data):
        try:
            req = request("POST", url=f"{env('PASI_ENDPOINT')}/api/v1/fouls/ExtendFoulDueDate",
                          verify=False,
                          headers={'content-type': 'application/json', 'x-api-version': '1.0'},
                          json={
                              "username": "string",
                              "password": "string",
                              "customerID": {
                                  "id": "string",
                                  "type": 0
                              },
                              "customerLanguage": 0,
                              "customerIPAddress": "string",
                              "foulNumber": foul_data.foul_number,
                              "registerNumber": f"{foul_data.register_number}"
                          })
            return req
        except Exception as error:
            return {"status_code": 500, "error": error}
