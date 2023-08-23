from datetime import date
from pydantic import BaseModel


class ReportInfo(BaseModel):
    formatted_date: str
    transaction_type: int
    total: int


class ReportMonthlyInfo(BaseModel):
    formatted_date: date
    transaction_type: int
    total: int


class ReportLabelInfo(BaseModel):
    label_name: str
    transaction_type: int
    total: int
