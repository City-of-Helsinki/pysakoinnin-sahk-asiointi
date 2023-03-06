from enum import Enum
from typing import Optional

from ninja import Schema


# Parking foul related
class FoulSchema(Schema):
    description: str
    additionalInfo: str


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
    vehicleModel: str
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
    referenceNumber: str
    iban: str
    barCode: str
    foulMakerAddress: Optional[str]
    attachments: list[AttachmentWithType]
    dueDateExtendable: bool
    dueDateExtendableReason: int
    responseCode: int


class ExtendDueDateResponse(Schema):
    success: bool
    errorcode: Optional[str]
    internalErrorDescription: Optional[str]
    dueDate: str
    dueDateExtendableReason: int
    responseCode: int


class AddressField(Schema):
    addressLine1: str
    addressLine2: str
    streetAddress: str
    postCode: str
    postOffice: str
    countryName: str


class Objection(Schema):
    foulNumber: int
    transferNumber: int
    folderID: str
    ssn: str
    firstName: str
    lastName: str
    email: str
    mobilePhone: str
    bic: str
    iban: str
    authorRole: int
    address: AddressField
    description: str
    attachments: list[AttachmentSchema]
    type: int
    sendDecisionViaEService: bool


class TransferDataResponse(Schema):
    transferNumber: int
    transferDate: str
    registerNumber: str
    vehicleType: str
    vehicleModel: str
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
    referenceNumber: Optional[str]
    iban: Optional[str]
    barCode: str
    vehicleOwnerAddress: Optional[str]
    attachments: list
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
    user_id: str
    transaction_id: str
    business_id: str
    tos_function_id: str
    tos_record_id: str
    metadata: dict
    content: dict
    draft: bool
    locked_after: Optional[str]
    deletable: bool
    attachments: list


class ATVDocumentResponse(Schema):
    count: int
    next: Optional[int]
    previous: Optional[int]
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
