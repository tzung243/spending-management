from pydantic import BaseModel


class LabelTransactionCreate(BaseModel):
    label_name: str
