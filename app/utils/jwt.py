import jwt
from datetime import datetime, timedelta, timezone
from app.config.settings import settings


def _parse_exp(value: str) -> timedelta:
    n = int(value[:-1])
    unit = value[-1]

    return {
        'm': timedelta(minutes=n),
        'h': timedelta(hours=n),
        'd': timedelta(days=n),
    }[unit]


from typing import Any

def generate_access_token(user_id: Any, payload: dict | None = None) -> str:
    token_payload = {
        "sub": str(user_id),
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + _parse_exp(settings.JWT_ACCESS_EXPIRES_IN),
    }
    if payload:
        token_payload.update(payload)
    return jwt.encode(token_payload, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Access token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid access token")


def generate_refresh_token(user_id: Any) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + _parse_exp(settings.JWT_REFRESH_EXPIRES_IN),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_refresh_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")
