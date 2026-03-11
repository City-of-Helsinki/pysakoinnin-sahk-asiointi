from enum import Enum, StrEnum


class Operation(Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Role(Enum):
    OWNER = "OWNER"
    USER = "USER"
    SYSTEM = "SYSTEM"
    ANONYMOUS = "ANONYMOUS"


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FORBIDDEN = "FORBIDDEN"


class DocumentStatusEnum(StrEnum):
    sent = "sent"
    received = "received"
    handling = "handling"
    resolvedViaEService = "resolvedViaEService"  # noqa: N815
    resolvedViaMail = "resolvedViaMail"  # noqa: N815
