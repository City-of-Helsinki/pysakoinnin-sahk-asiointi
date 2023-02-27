from typing import Optional

from ninja import Schema


# Parking foul related
class FoulSchema(Schema):
    description: str
    additionalInfo: str


class AttachmentSchema(Schema):
    attachmentType: int
    fileName: str
    mimeType: str
    data: str


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
    foulMakerAddress: str
    attachments: list[AttachmentSchema]
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
