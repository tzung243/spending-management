from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import Users


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    return {"message": "Hello World"}
