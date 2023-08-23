from fastapi import Depends, APIRouter, HTTPException, Request
from sqlalchemy import and_, text
from sqlalchemy.orm import Session
from app.schema.transaction import (
    TranferWallet,
    TransactionCreate,
    TransactionInfo,
    TransactionUpdate,
)
from app.security import validate_token, get_user
from app.database import get_db
from app.database.models import TransactionLabels, Transactions, Wallets

router = APIRouter(prefix="/transaction", tags=["Transaction"])
from datetime import datetime
from app.constans import TransactionType, TransactionLabel


@router.get("/", dependencies=[Depends(validate_token)])
def get_all_transactions(
    sort_col: str,
    sort_order: str,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    query = """
    SELECT transactions.id, transactions.type, transactions.amount,
       transactions.description, transactions.date, wallets.name AS wallet_name,
       transaction_labels.label_name
    FROM transactions
    left join wallets on transactions.wallet_id = wallets.id
    left join transaction_labels on transactions.label = transaction_labels.id
    where transactions.user_id = :user_id
    ORDER BY transactions.{0} {1}
    """.format(
        sort_col, sort_order
    )
    result = db.execute(
        text(query),
        {"user_id": user_info["user_id"]},
    ).fetchall()
    transactions = [TransactionInfo(**row._asdict()) for row in result]
    return transactions


@router.get("/income/{date}", dependencies=[Depends(validate_token)])
def get_transaction_income(
    date: str,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    query = """
    SELECT transactions.id, transactions.type, transactions.amount,
       transactions.description, transactions.date, wallets.name AS wallet_name,
       transaction_labels.label_name
    FROM transactions
    left join wallets on transactions.wallet_id = wallets.id
    left join transaction_labels on transactions.label = transaction_labels.id
    where transactions.user_id = :user_id and transactions.type = 1 and date(transactions.date) = :date
    ORDER BY transactions.date DESC
    """
    result = db.execute(
        text(query), {"user_id": user_info["user_id"], "date": date}
    ).fetchall()
    transactions = [TransactionInfo(**row._asdict()) for row in result]

    return transactions


@router.get("/expense/{date}", dependencies=[Depends(validate_token)])
def get_transaction_expense(
    date: str,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    query = """
    SELECT transactions.id, transactions.type, transactions.amount,
       transactions.description, transactions.date, wallets.name AS wallet_name,
       transaction_labels.label_name
    FROM transactions
    left join wallets on transactions.wallet_id = wallets.id
    left join transaction_labels on transactions.label = transaction_labels.id
    where transactions.user_id = :user_id and transactions.type = 2 and date(transactions.date) = :date
    ORDER BY transactions.date DESC
    """
    result = db.execute(
        text(query), {"user_id": user_info["user_id"], "date": date}
    ).fetchall()
    transactions = [TransactionInfo(**row._asdict()) for row in result]

    return transactions


@router.get("/summary", dependencies=[Depends(validate_token)])
def get_summary_transactions(
    user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    query = """
    SELECT sum(transactions.amount) as expense_month
    FROM transactions
    where transactions.user_id = :user_id and month(transactions.date) = month(now()) and type = 2
    """
    expense_month = db.execute(
        text(query), {"user_id": user_info["user_id"]}
    ).fetchall()

    query = """
    SELECT sum(transactions.amount) as expense_today
    from transactions
    where transactions.user_id = :user_id and date(transactions.date) = date(now()) and type = 2
    """
    expense_today = db.execute(
        text(query), {"user_id": user_info["user_id"]}
    ).fetchall()
    return {
        "expense_month": expense_month[0][0] if expense_month[0][0] else 0,
        "expense_today": expense_today[0][0] if expense_today[0][0] else 0,
    }


@router.post("/", dependencies=[Depends(validate_token)])
def create_transaction(
    request: TransactionCreate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    wallet = db.query(Wallets).filter(Wallets.id == request.wallet_id).first()
    if not wallet or wallet.user_id != user_info["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid transaction")

    label = (
        db.query(TransactionLabels)
        .filter(TransactionLabels.id == request.label_id)
        .first()
    )
    if not label:
        raise HTTPException(status_code=400, detail="Invalid transaction")

    if request.type == TransactionType.EXPENSE:
        if wallet.amount < request.amount:
            raise HTTPException(status_code=400, detail="Invalid transaction")
        wallet.amount -= request.amount
    elif request.type == TransactionType.INCOME:
        wallet.amount += request.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction")
    transaction = Transactions(
        user_id=user_info["user_id"],
        wallet_id=request.wallet_id,
        amount=request.amount,
        type=request.type,
        description=request.description,
        date=datetime.strptime(request.date, "%Y-%m-%d %H:%M:%S"),
        label=request.label_id,
    )
    db.add(transaction)
    db.commit()
    return {
        "user_id": transaction.user_id,
        "wallet_id": wallet.name,
        "amount": transaction.amount,
        "type": transaction.type,
        "description": transaction.description,
        "date": transaction.date,
        "label": transaction.label,
    }


@router.put("/{id}", dependencies=[Depends(validate_token)])
def update_transaction(
    id: int,
    request: TransactionUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(Transactions)
        .filter(
            and_(
                Transactions.id == id,
                Transactions.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if not transaction or transaction.user_id != user_info["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid request")

    if {
        k: v for k, v in transaction.__dict__.items() if k in request.__dict__.keys()
    } == request.__dict__:
        raise HTTPException(status_code=400, detail="Nothing to update")
    wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()
    if request.wallet_id != None and request.wallet_id != transaction.wallet_id:
        new_wallet = (
            db.query(Wallets)
            .filter(
                Wallets.id == request.wallet_id, Wallets.user_id == user_info["user_id"]
            )
            .first()
        )
        if not new_wallet:
            raise HTTPException(status_code=400, detail="Invalid request")
        if transaction.wallet_id != request.wallet_id:
            if transaction.type == TransactionType.EXPENSE:
                wallet.amount += transaction.amount
                new_wallet.amount -= transaction.amount
            elif transaction.type == TransactionType.INCOME:
                wallet.amount -= transaction.amount
                new_wallet.amount += transaction.amount
            else:
                raise HTTPException(status_code=400, detail="Invalid request")
            transaction.wallet_id = request.wallet_id
            db.commit()
    if request.type != None and request.type != transaction.type:
        wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()
        if request.type == TransactionType.EXPENSE:
            wallet.amount -= 2 * transaction.amount
        elif request.type == TransactionType.INCOME:
            wallet.amount += 2 * transaction.amount
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
        transaction.type = request.type
        db.commit()

    if request.amount != None and request.amount != transaction.amount:
        wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()
        if transaction.type == TransactionType.EXPENSE:
            if wallet.amount + transaction.amount < request.amount:
                raise HTTPException(status_code=400, detail="Invalid request")
            wallet.amount = wallet.amount - (request.amount - transaction.amount)
        elif transaction.type == TransactionType.INCOME:
            wallet.amount = wallet.amount + (request.amount - transaction.amount)
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
        transaction.amount = request.amount
        db.commit()

    if request.description:
        transaction.description = request.description
    if request.date:
        transaction.date = datetime.strptime(request.date, "%Y-%m-%d %H:%M:%S")
    if request.label:
        transaction.label = request.label
    db.commit()
    return {"message": "Transaction updated successfully"}


@router.delete("/{id}", dependencies=[Depends(validate_token)])
def delete_transaction(
    id: int, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    transaction = (
        db.query(Transactions)
        .filter(
            and_(Transactions.id == id, Transactions.user_id == user_info["user_id"])
        )
        .first()
    )

    if not transaction or transaction.user_id != user_info["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid request")
    wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()
    if int(transaction.type) == TransactionType.EXPENSE:
        wallet.amount += transaction.amount
    elif int(transaction.type) == TransactionType.INCOME:
        wallet.amount -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@router.post("/transfer", dependencies=[Depends(validate_token)])
def transfer(
    request: TranferWallet,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    wallet_transfer = db.query(Wallets).filter(Wallets.id == request.wallet_id).first()
    wallet_receiv = db.query(Wallets).filter(Wallets.id == request.label).first()
    if not wallet_transfer or not wallet_receiv:
        raise HTTPException(status_code=400, detail="Invalid transaction")
    if (
        wallet_transfer.user_id != user_info["user_id"]
        or wallet_receiv.user_id != user_info["user_id"]
    ):
        raise HTTPException(status_code=400, detail="Invalid transaction")

    if wallet_transfer.amount < request.amount:
        raise HTTPException(status_code=400, detail="Invalid transaction")

    wallet_transfer.amount -= request.amount
    wallet_receiv.amount += request.amount

    if request.fee:
        wallet_transfer.amount -= request.fee

    transaction = TransactionCreate(
        wallet_id=request.waller_transfer,
        amount=request.fee,
        date=request.date,
        type=TransactionType.EXPENSE,
        label=TransactionLabel.TRANSFER,
        description=request.description,
    )
    create_transaction(transaction, user_info, db)
    db.commit()
    return {"message": "Transaction created successfully"}


@router.get("/{transaction_id}", dependencies=[Depends(validate_token)])
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    querry = """
    SELECT transactions.id, transactions.type, transactions.amount,
       transactions.description, transactions.date, wallets.name AS wallet_name,
       transaction_labels.label_name
    FROM transactions
    left join wallets on transactions.wallet_id = wallets.id
    left join transaction_labels on transactions.label = transaction_labels.id
    where transactions.id = :id
    """

    transaction = db.execute(text(querry), {"id": transaction_id}).fetchall()
    if not transaction:
        raise HTTPException(status_code=400, detail="Invalid transaction")
    response = [TransactionInfo(**row._asdict()) for row in transaction]
    return response[0]
