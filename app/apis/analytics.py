from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, text

from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import Wallets as DBWallets
from app.schema.report import ReportInfo, ReportLabelInfo, ReportMonthlyInfo
from app.schema.wallet import WalletCreate, WalletUpdate
from app.security import get_user, validate_token

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/report", dependencies=[Depends(validate_token)])
def get_report(user_info: dict = Depends(get_user), db: Session = Depends(get_db)):
    query = """
    SELECT DATE(date) AS formatted_date, type as transaction_type, sum(amount) as total
    FROM transactions
    where user_id = :user_id
    group by type, DATE(date)
    """
    report = db.execute(text(query), {"user_id": user_info["user_id"]}).fetchall()
    response = [ReportMonthlyInfo(**row._asdict()) for row in report]
    return {"transactions": response}


@router.get("/monthly", dependencies=[Depends(validate_token)])
def analytic(user_info: dict = Depends(get_user), db: Session = Depends(get_db)):
    current_year = datetime.now().year

    query = """
    SELECT DATE_FORMAT(date, '%Y-%m') AS formatted_date, type AS transaction_type, SUM(amount) AS total
    FROM transactions
    WHERE user_id = :user_id AND YEAR(date) = :year
    GROUP BY formatted_date, transaction_type
    """
    report = db.execute(
        text(query), {"user_id": user_info["user_id"], "year": current_year}
    ).fetchall()
    response = [ReportInfo(**row._asdict()) for row in report]
    return response


@router.get("/label", dependencies=[Depends(validate_token)])
def analytic(user_info: dict = Depends(get_user), db: Session = Depends(get_db)):
    current_year = datetime.now().year

    query = """
    Select label_name, type as transaction_type, sum(amount) as total
    from transactions
    left join transaction_labels on transactions.label = transaction_labels.id
    where transactions.user_id = :user_id and YEAR(date) = :year
    group by label, type
    """

    report = db.execute(
        text(query), {"user_id": user_info["user_id"], "year": current_year}
    ).fetchall()
    response = [ReportLabelInfo(**row._asdict()) for row in report]
    return response


@router.get("/label/{label_id}", dependencies=[Depends(validate_token)])
def analytics_by_label(
    label_id: int, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    current_year = datetime.now().year
    query = """
    SELECT DATE_FORMAT(date, '%Y-%m') AS formatted_date, type AS transaction_type, SUM(amount) AS total
    FROM transactions
    WHERE user_id = :user_id AND YEAR(date) = :year and label = :label_id
    GROUP BY formatted_date, transaction_type 
    """
    report = db.execute(
        text(query),
        {"user_id": user_info["user_id"], "year": current_year, "label_id": label_id},
    ).fetchall()
    response = [ReportInfo(**row._asdict()) for row in report]
    return response
