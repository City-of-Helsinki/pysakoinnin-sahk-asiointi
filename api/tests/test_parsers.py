from django.utils.datastructures import MultiValueDict

from api.parsers import StripParser


def test_strip_parser_removes_whitespace_from_query_dict(rf):
    parser = StripParser()
    data = MultiValueDict({"key1": [" value1 "]})

    result = parser.parse_querydict(data, ["key2"], rf.get("/"))

    assert result == {"key1": "value1"}


def test_strip_parser_removes_whitespace_from_request_body(rf):
    parser = StripParser()
    data = {"key1": " value1 ", "key2": " value2 "}
    request = rf.post("/", data, content_type="application/json")

    result = parser.parse_body(request)

    assert result == {"key1": "value1", "key2": "value2"}
