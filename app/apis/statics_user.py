from fastapi import APIRouter, Depends, HTTPException
from app.security import generate_token
from app.security import get_user, validate_token
from app.database import get_db
from sqlalchemy.orm import Session
from app.constans import StaticsType
from sqlalchemy import text
router = APIRouter(prefix="/statics", tags=["Statics"])


@router.get("/", dependencies=[Depends(validate_token)])
def get_statics(
    type: int,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    querry_t = None
    if type == StaticsType.MONTH:
        querry_t = """
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, COUNT(*) AS count
            FROM transactions
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND user_id = :user_id
            GROUP BY month;
        """
    elif type == StaticsType.DAYS:
        querry_t = """
            SELECT DATE_FORMAT(date, '%Y-%m-%d') AS day, COUNT(*) AS count
            FROM transactions
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) -- Lọc từ ngày hiện tại trở về sau 3 tháng
            GROUP BY day;
        """
    if querry_t is None:
        raise HTTPException(status_code=400, detail="Invalid type")
    params = {"user_id": user_info["user_id"]}
    result = db.execute(text(querry_t), params).fetchall()
    return {result}