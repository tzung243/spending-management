from pydantic import BaseModel
from typing import Optional
from app.constans import WalletType


class WalletCreate(BaseModel):
    name: str
    type: Optional[int] = WalletType.CASH
    amount: Optional[int] = 0


class WalletUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[int] = None
    amount: Optional[int] = None
