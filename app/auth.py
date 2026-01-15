import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

# Load values from the .env file
load_dotenv()

def require_api_key(x_api_key: str | None = Header(default=None)):
    expected_key = os.getenv("API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="API_KEY not set on server"
        )

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )