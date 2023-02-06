import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .services.swift import SwiftService, TransactionNotFound, SwiftServiceUnavailable


is_prod = os.environ.get("ENVIRONMENT") == "production"


app = FastAPI(
    title="Swift Transaction Status API",
    docs_url="/api/docs" if not is_prod else None,
    redoc_url=None,
)


swift_service = SwiftService()


@app.get("/api/transactions/{uetr}")
async def get_transaction_details(uetr):
    auth_token = swift_service.get_auth_token()

    try:
        data = swift_service.get_transaction_details(auth_token, uetr)
        return data
    except TransactionNotFound:
        raise HTTPException(status_code=404, detail="Invalid UETR")
    except SwiftServiceUnavailable:
        raise HTTPException(status_code=503, detail="Swift API unavailable")


if is_prod:
    app.mount(
        "/", StaticFiles(directory="/etc/swift_demo/static", html=True), name="ui"
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
