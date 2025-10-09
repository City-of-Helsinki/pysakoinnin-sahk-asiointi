from enum import Enum
from typing import Optional

from ninja import Schema
from pydantic import Field


# Parking foul related
class FoulSchema(Schema):
    description: str
    additionalInfo: Optional[str] = None


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
    vehicleModel: Optional[str] = None
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
    referenceNumber: Optional[str] = None
    iban: Optional[str] = None
    barCode: Optional[str] = None
    foulMakerAddress: Optional[str] = None
    attachments: list[AttachmentWithType] = Field(default_factory=list)
    dueDateExtendable: bool
    dueDateExtendableReason: int
    responseCode: int


class ExtendDueDateResponse(Schema):
    success: bool
    errorcode: Optional[str] = None
    internalErrorDescription: Optional[str] = None
    dueDate: str
    dueDateExtendableReason: int
    responseCode: int


class FoulRequest(Schema):
    foul_number: int
    register_number: str
    metadata: Optional[dict] = None


class AddressField(Schema):
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    streetAddress: str
    postCode: str
    postOffice: Optional[str] = None
    countryName: Optional[str] = None


class Objection(Schema):
    foulNumber: Optional[int] = None
    transferNumber: Optional[int] = None
    folderID: Optional[str] = None
    ssn: str
    firstName: str
    lastName: str
    email: str
    mobilePhone: str
    bic: Optional[str] = None
    iban: str
    authorRole: int
    address: AddressField
    description: str
    attachments: Optional[list[AttachmentSchema]] = None
    type: int
    sendDecisionViaEService: bool
    metadata: Optional[dict] = None


class TransferDataResponse(Schema):
    transferNumber: int
    transferDate: str
    registerNumber: str
    vehicleType: str
    vehicleModel: Optional[str] = None
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
    referenceNumber: Optional[str] = None
    iban: Optional[str] = None
    barCode: Optional[str] = None
    vehicleOwnerAddress: Optional[str] = None
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
    user_id: Optional[str] = None
    transaction_id: str
    business_id: str
    tos_function_id: str
    tos_record_id: str
    metadata: dict
    content: dict
    draft: bool
    locked_after: Optional[str] = None
    deletable: bool
    delete_after: Optional[str] = None
    attachments: list


class ATVDocumentResponse(Schema):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
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
