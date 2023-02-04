import base64
from datetime import datetime
import jwt
import math
import random
import re
import requests
import os

from dotenv import load_dotenv


load_dotenv('.env')

BASE_URL="https://sandbox.swift.com"
SWIFT_CONSUMER_KEY = os.environ.get('SWIFT_CONSUMER_KEY')
SWIFT_CONSUMER_SECRET = os.environ.get('SWIFT_CONSUMER_SECRET')


def get_jti():
    values = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join([random.choice(values) for i in range(0, 12)])


def get_auth_token():
    with open("private-key.pem") as f:
        private_key_pem = f.read()

    with open("certificate.pem") as f:
        cert_pem = re.sub(r"(\r\n|\n|\r)", "", f.read()[27:])
        cert_pem = cert_pem[:len(cert_pem) - 25]

    headers = {
        "typ": "JWT",
        "alg": "RS256",
        "x5c": [cert_pem]
    }

    jti = get_jti()

    current_time = datetime.now()
    issued_at = math.ceil(current_time.timestamp())
    expiration = issued_at + 900

    payload = {
        "iss": f"{BASE_URL}/oauth2/v1/token",
        "aud": f"{BASE_URL}/oauth2/v1/token",
        "sub": "CN=desktop, O=sandbox, O=swift",
        "jti": jti,
        "exp" : expiration,
        "iat" : issued_at,
    }

    jwt_token = jwt.encode(payload, private_key_pem, algorithm="RS256", headers=headers)

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
            "assertion": jwt_token
        }
    )

    return request.json()["access_token"]


def get_transaction_details(auth_token, uetr):
    url = f"{BASE_URL}/swift-apitracker/v4/payments/{uetr}/transactions"
    request = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
    return request.json()

