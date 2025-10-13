from enum import Enum

from ninja import Schema
from pydantic import Field


# Parking foul related
class FoulSchema(Schema):
    description: str
    additionalInfo: str | None = None


class AttachmentSchema(Schema):
    fileName: str
    mimeType: str
    data: str


class AttachmentWithType(AttachmentSchema):
    attachmentType: int


class FoulDataResponse(Schema):
    foulNumber: int
    foulDate: str
    monitoringStart: str
    registerNumber: str
    vehicleType: str
    vehicleModel: str | None = None
    vehicleBrand: str
    vehicleColor: str
    address: str
    addressAdditionalInfo: str
    x_Coordinate: str
    y_Coordinate: str
    description: str
    fouls: list[FoulSchema]
    invoiceSumText: str
    openAmountText: str
    dueDate: str
    referenceNumber: str | None = None
    iban: str | None = None
    barCode: str | None = None
    foulMakerAddress: str | None = None
    attachments: list[AttachmentWithType] = Field(default_factory=list)
    dueDateExtendable: bool
    dueDateExtendableReason: int
    responseCode: int


class ExtendDueDateResponse(Schema):
    success: bool
    errorcode: str | None = None
    internalErrorDescription: str | None = None
    dueDate: str
    dueDateExtendableReason: int
    responseCode: int


class FoulRequest(Schema):
    foul_number: int
    register_number: str
    metadata: dict | None = None


class AddressField(Schema):
    addressLine1: str | None = None
    addressLine2: str | None = None
    streetAddress: str
    postCode: str
    postOffice: str | None = None
    countryName: str | None = None


class Objection(Schema):
    foulNumber: int | None = None
    transferNumber: int | None = None
    folderID: str | None = None
    ssn: str
    firstName: str
    lastName: str
    email: str
    mobilePhone: str
    bic: str | None = None
    iban: str
    authorRole: int
    address: AddressField
    description: str
    attachments: list[AttachmentSchema] | None = None
    type: int
    sendDecisionViaEService: bool
    metadata: dict | None = None


class TransferDataResponse(Schema):
    transferNumber: int
    transferDate: str
    registerNumber: str
    vehicleType: str
    vehicleModel: str | None = None
    vehicleBrand: str
    vehicleColor: str
    startAddress: str
    startAddressAdditionalInfo: str
    endAddress: str
    endAddressAdditionalInfo: str
    x_Coordinate: str
    y_Coordinate: str
    description: str
    fouls: list
    invoiceSumText: str
    openAmountText: str
    dueDate: str
    referenceNumber: str | None = None
    iban: str | None = None
    barCode: str | None = None
    vehicleOwnerAddress: str | None = None
    attachments: list = Field(default_factory=list)
    vehicleChassisNumber: str
    transferStartDate: str
    transferEndDate: str
    transferType: str
    transferStatus: str
    transferReason: str
    foulTypes: list
    responseCode: int


# ATV related
class ATVDocumentSchema(Schema):
    id: str
    created_at: str
    updated_at: str
    status: dict
    status_histories: list
    type: str
    human_readable_type: dict
    service: str
    user_id: str | None = None
    transaction_id: str
    business_id: str
    tos_function_id: str
    tos_record_id: str
    metadata: dict
    content: dict
    draft: bool
    locked_after: str | None = None
    deletable: bool
    delete_after: str | None = None
    attachments: list


class ATVDocumentResponse(Schema):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[ATVDocumentSchema]


class DocumentStatusEnum(str, Enum):
    sent = "sent"
    received = "received"
    handling = "handling"
    resolvedViaEService = "resolvedViaEService"
    resolvedViaMail = "resolvedViaMail"


class DocumentStatusRequest(Schema):
    id: str
    status: DocumentStatusEnum
