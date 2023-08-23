from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, desc, or_
from app.database import get_db
from app.database.models import TransactionLabels
from app.schema.label import LabelTransactionCreate
from app.security import validate_token, get_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/transaction_label", tags=["Transaction Label"])


@router.post("/", dependencies=[Depends(validate_token)])
def create_label_transaction(
    request: LabelTransactionCreate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    label_name = request.label_name.upper()
    label = (
        db.query(TransactionLabels)
        .filter(
            and_(
                TransactionLabels.label_name == label_name,
                TransactionLabels.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if label:
        raise HTTPException(status_code=400, detail="Label name already exists")

    label = TransactionLabels(label_name=label_name, user_id=user_info["user_id"])
    db.add(label)
    db.commit()
    return {label.label_name}


@router.get("/{id}", dependencies=[Depends(validate_token)])
def get_label_by_id(id: int, db: Session = Depends(get_db)):
    label = db.query(TransactionLabels).filter(and_(TransactionLabels.id == id)).first()
    if label is None:
        raise HTTPException(status_code=400, detail="Label not found")
    return label


@router.get("/", dependencies=[Depends(validate_token)])
def get_all_label(user_info: dict = Depends(get_user), db: Session = Depends(get_db)):
    labels = (
        db.query(TransactionLabels)
        .filter(
            or_(
                TransactionLabels.user_id == user_info["user_id"],
                TransactionLabels.user_id == None,
            )
        )
        .order_by(desc(TransactionLabels.id))
        .all()
    )
    if labels is None:
        return []
    # labels = [label.label_name for label in labels]
    return labels


@router.put("/{id}", dependencies=[Depends(validate_token)])
def update_label(
    id: int,
    body: LabelTransactionCreate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    label = (
        db.query(TransactionLabels)
        .filter(
            and_(
                TransactionLabels.id == id,
                TransactionLabels.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if label is None:
        raise HTTPException(status_code=400, detail="Label not found")
    label.label_name = body.label_name.upper()
    db.commit()
    return {"message": "Label updated successfully"}


@router.delete("/{label_name}", dependencies=[Depends(validate_token)])
def delete_label(
    label_name: str, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    labels = (
        db.query(TransactionLabels)
        .filter(
            and_(
                TransactionLabels.label_name == label_name,
                TransactionLabels.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if labels is None:
        raise HTTPException(status_code=400, detail="It's default label")
    db.delete(labels)
    db.commit()
    return {"message": "Label deleted successfully"}


# @router.put("{label_name}", dependencies=[Depends(validate_token)])
# def update_label(
