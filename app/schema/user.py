from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: str
