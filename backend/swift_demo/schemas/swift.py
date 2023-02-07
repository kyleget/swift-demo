from datetime import datetime
from enum import Enum
from uuid import UUID

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, validator, EmailStr


class TransactionStatus(str, Enum):
    accepted = "accepted"
    completed = "completed"
    rejected = "rejected"
    unknown = "unknown"


class Amount(BaseModel):
    amount: str
    currency: str
    formatted_amount: str


class PaymentEvent(BaseModel):
    fees: Amount
    from_: str
    instructed_amount: Amount | None
    last_update_date: datetime
    message_type: str
    received_date: datetime
    settlement_amount: Amount | None
    to: str
    transaction_status_reason: str | None
    transaction_status: TransactionStatus
    uetr: str

    class Config:
        fields = {"from_": "from"}


class TransactionDetails(BaseModel):
    bank: str
    completion_date: datetime | None
    currency: str | None
    formatted_amount: str | None
    initiation_date: datetime
    last_update_date: datetime | None
    payment_events: list[PaymentEvent]
    settlement_amount: Amount | None
    transaction_status: TransactionStatus
