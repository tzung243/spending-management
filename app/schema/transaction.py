from pydantic import BaseModel
from typing import Optional


class TransactionCreate(BaseModel):
    wallet_id: int
    amount: int
    type: int
    description: Optional[str] = None
    date: str
    label: Optional[int] = None


class TransactionUpdate(BaseModel):
    id: int
    wallet_id: Optional[int] = None
    amount: Optional[int] = 0
    type: Optional[int] = None
    description: Optional[str] = None
    date: Optional[str] = None
    label: Optional[int] = None


class TranferWallet(BaseModel):
    waller_transfer: int
    wallet_receiv: int
    amount: int
    date: str
    description: Optional[str] = None
    fee: Optional[int] = 0
