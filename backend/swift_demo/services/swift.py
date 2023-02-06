import base64
from datetime import datetime
from decimal import Decimal
import dateutil.parser as dt
import jwt
import math
from operator import itemgetter
import random
import re
import requests
import os

from dotenv import load_dotenv

from ..schemas.swift import Amount, TransactionDetails, TransactionStatus

load_dotenv(".env")

BASE_URL = "https://sandbox.swift.com"
SWIFT_CONSUMER_KEY = os.environ.get("SWIFT_CONSUMER_KEY")
SWIFT_CONSUMER_SECRET = os.environ.get("SWIFT_CONSUMER_SECRET")
CERTIFICATE_PATH = os.environ.get("CERTIFICATE_PATH")
PRIVATE_KEY_PATH = os.environ.get("PRIVATE_KEY_PATH")


def _get_transaction_status_reason(reason_code: str) -> str:
    reason_map = {
        "G000": "The Status Originator transferred the Credit Transfer to the next Agent or to a Market Infrastructure maintaining the transaction's service obligations.",
        "G001": "The Status Originator transferred the Credit Transfer to the next Agent or to a Market Infrastructure where the transaction's service obligations may no longer be guaranteed.",
        "G002": "The transaction processing cannot be completed the same day.",
        "G003": "In an FI to FI Customer Credit Transfer: Credit to creditor's account is pending receipt of required documents. The Status Originator has requested creditor to provide additional documentation.",
        "G004": "Credit to the creditor's account is pending as status Originator is waiting for funds provided via a cover.",
        "G005": "Credit Transfer has been delivered to creditor agent with transaction's service obligations maintained.",
        "G006": "Credit Transfer has been delivered to creditor agent where the transaction's service obligations were no longer maintained.",
    }
    return reason_map.get(reason_code, None)


def _get_transaction_status(status_code: str) -> TransactionStatus:
    status_map = {
        "ACCC": TransactionStatus.completed,
        "ACSP": TransactionStatus.accepted,
        "RJCT": TransactionStatus.rejected,
    }
    return status_map.get(status_code, TransactionStatus.unknown)


def _get_formatted_amount(amount: str, currency: str):
    return "{:,} {}".format(Decimal(amount), currency)


def _get_fees(charge_amount):
    amount = Decimal("0.00")
    currency = None

    for c in charge_amount:
        amount = amount + Decimal(c["amount"])
        assert c["currency"] == currency or currency == None
        currency = c["currency"]

    formatted_amount = _get_formatted_amount(amount, currency)

    return {
        "amount": f"{amount:.2f}",
        "currency": currency,
        "formatted_amount": formatted_amount,
    }


def _get_payment_events(swift_payment_events):
    payment_events = []
    amount = None
    currency = None
    formatted_amount = None
    bank = None

    for pe in swift_payment_events:
        settlement_amount = pe.get("interbank_settlement_amount")

        if pe["message_name_identification"] == "199":
            bank = pe["originator"]

            if settlement_amount:
                amount = settlement_amount["amount"]
                currency = settlement_amount["currency"]
                formatted_amount = _get_formatted_amount(amount, currency)

        payment_events.append(
            {
                "fees": _get_fees(
                    pe["charge_amount"] if "charge_amount" in pe else None
                ),
                "from": pe["from"],
                "instructed_amount": {
                    "amount": pe["instructed_amount"]["amount"],
                    "currency": pe["instructed_amount"]["currency"],
                    "formatted_amount": _get_formatted_amount(
                        pe["instructed_amount"]["amount"],
                        pe["instructed_amount"]["currency"],
                    ),
                }
                if "instructed_amount" in pe
                else None,
                "last_update_date": pe["last_update_time"],
                "message_type": f"MT{pe['message_name_identification']}",
                "received_date": dt.parse(pe["received_date"]),
                "settlement_amount": {
                    "amount": settlement_amount["amount"]
                    if settlement_amount
                    else None,
                    "currency": settlement_amount["currency"]
                    if settlement_amount
                    else None,
                    "formatted_amount": _get_formatted_amount(
                        settlement_amount["amount"], settlement_amount["currency"]
                    ),
                }
                if settlement_amount
                else None,
                "to": pe["to"],
                "transaction_status_reason": _get_transaction_status_reason(
                    pe["transaction_status_reason"]
                )
                if "transaction_status_reason" in pe
                else None,
                "transaction_status": _get_transaction_status(pe["transaction_status"]),
            }
        )

    return {
        "amount": {
            "amount": amount,
            "currency": currency,
            "formatted_amount": formatted_amount,
        },
        "bank": bank,
        "payment_events": payment_events,
    }


def create_jti():
    values = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join([random.choice(values) for i in range(0, 12)])


class TransactionNotFound(Exception):
    pass


class SwiftServiceUnavailable(Exception):
    pass


class SwiftService:
    def get_auth_token(self):
        with open(PRIVATE_KEY_PATH) as f:
            private_key_pem = f.read()

        with open(CERTIFICATE_PATH) as f:
            cert_pem = re.sub(r"(\r\n|\n|\r)", "", f.read()[27:])
            cert_pem = cert_pem[: len(cert_pem) - 25]

        headers = {"typ": "JWT", "alg": "RS256", "x5c": [cert_pem]}

        jti = create_jti()

        current_time = datetime.now()
        issued_at = math.ceil(current_time.timestamp())
        expiration = issued_at + 900

        payload = {
            "iss": f"{BASE_URL}/oauth2/v1/token",
            "aud": f"{BASE_URL}/oauth2/v1/token",
            "sub": "CN=desktop, O=sandbox, O=swift",
            "jti": jti,
            "exp": expiration,
            "iat": issued_at,
        }

        jwt_token = jwt.encode(
            payload, private_key_pem, algorithm="RS256", headers=headers
        )

        url = f"{BASE_URL}/oauth2/v1/token"

        message = f"{SWIFT_CONSUMER_KEY}:{SWIFT_CONSUMER_SECRET}"
        message_bytes = message.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")

        request = requests.post(
            url,
            headers={
                "Authorization": f"Basic {base64_message}",
            },
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "scope": "swift.apitracker",
                "assertion": jwt_token,
            },
        )

        return request.json()["access_token"]

    def get_transaction_details(self, auth_token, uetr):
        url = f"{BASE_URL}/swift-apitracker/v4/payments/{uetr}/transactions"
        request = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
        data = request.json()

        code = data.get("code")

        if code == "SwAP010":
            raise SwiftServiceUnavailable()

        if code == "Sw.gpi.NoResultFound":
            raise TransactionNotFound()

        amount, bank, payment_events = itemgetter("amount", "bank", "payment_events")(
            _get_payment_events(data["payment_event"])
        )

        details: TransactionDetails = {
            "bank": bank,
            "completion_date": dt.parse(data.get("completion_time")),
            "initiation_date": dt.parse(data.get("initiation_time")),
            "last_update_date": dt.parse(data.get("last_update_time")),
            "payment_events": payment_events,
            "settlement_amount": amount,
            "transaction_status": _get_transaction_status(data["transaction_status"]),
            "uetr": data["uetr"],
        }

        return data

        return details
