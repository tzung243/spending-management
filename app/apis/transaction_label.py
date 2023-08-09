from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.database.models import TransactionLabels
from app.security import validate_token, get_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/transaction_label", tags=["Transaction Label"])


@router.post("/", dependencies=[Depends(validate_token)])
def create_label_transaction(
    label_name: str, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    label = (
        db.query(TransactionLabels).filter(TransactionLabels.name == label_name).first()
    )
    if label:
        raise HTTPException(status_code=400, detail="Label name already exists")

    label = TransactionLabels(name=label_name, user_id=user_info["user_id"])
    db.add(label)
    db.commit()
    return {"message": "Label created successfully"}
