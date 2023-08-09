from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import ValidationError
from app.core.config import settings

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 3  # 3 days


def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> str:
    """
    Decode JWT token to get username => return username
    """
    try:
        payload = jwt.decode(
            http_authorization_credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM],
        )
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise HTTPException(status_code=403, detail="Token expired")
        return payload.get("username")
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )


def generate_token(username: Union[str, Any], user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "username": username, "user_id": user_id}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )
    return encoded_jwt


def get_user(token: str = Depends(reusable_oauth2)) -> dict:
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM],
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = {"user_id": user_id, "username": username}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data
