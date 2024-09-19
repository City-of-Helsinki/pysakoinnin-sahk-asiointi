from typing import List

from django.http import HttpRequest
from django.utils.datastructures import MultiValueDict
from ninja.parser import Parser
from ninja.types import DictStrAny


class StripParser(Parser):
    """Remove leading and trailing whitespaces from all string values."""

    def _strip_dict(self, data: DictStrAny) -> DictStrAny:
        return {
            key: value.strip() if isinstance(value, str) else value
            for key, value in data.items()
        }

    def parse_body(self, request: HttpRequest) -> DictStrAny:
        result = super().parse_body(request)
        return self._strip_dict(result)

    def parse_querydict(
        self, data: MultiValueDict, list_fields: List[str], request: HttpRequest
    ) -> DictStrAny:
        result = super().parse_querydict(data, list_fields, request)
        return self._strip_dict(result)
