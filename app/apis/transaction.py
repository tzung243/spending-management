from fastapi import Depends, APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from app.schema.transaction import TranferWallet, TransactionCreate, TransactionUpdate
from app.security import validate_token, get_user
from app.database import get_db
from app.database.models import TransactionLabels, Transactions, Wallets

router = APIRouter(prefix="/transaction", tags=["Transaction"])
from datetime import datetime
from app.constans import TransactionType, TransactionLabel


@router.get("/all", dependencies=[Depends(validate_token)])
def get_all_transactions(
    user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    transactions = (
        db.query(Transactions)
        .filter(Transactions.user_id == user_info["user_id"])
        .all()
    )
    return transactions


@router.get("/", dependencies=[Depends(validate_token)])
def get_transaction(
    transaction_id: int,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(Transactions)
        .filter(
            Transactions.id == transaction_id
            and Transactions.user_id == user_info["user_id"]
        )
        .first()
    )
    if transaction is None:
        raise HTTPException(status_code=400, detail="Transaction not found")
    return transaction


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
        .filter(TransactionLabels.id == request.label)
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
        label=request.label,
    )
    db.add(transaction)
    db.commit()
    return {"message": "Transaction created successfully"}


@router.put("/", dependencies=[Depends(validate_token)])
def update_transaction(
    request: TransactionUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    transaction = db.query(Transactions).filter(Transactions.id == request.id).first()
    if not transaction or transaction.user_id != user_info["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid request")

    wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()

    if request.wallet_id:
        new_wallet = db.query(Wallets).filter(Wallets.id == request.wallet_id).first()
        if not new_wallet or new_wallet.user_id != user_info["user_id"]:
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
    if request.amount:
        if transaction.type == TransactionType.EXPENSE:
            if wallet.amount + transaction.amount < request.amount:
                raise HTTPException(status_code=400, detail="Invalid request")
            wallet.amount = wallet.amount + transaction.amount - request.amount
        elif transaction.type == TransactionType.INCOME:
            wallet.amount = wallet.amount - transaction.amount + request.amount
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
        transaction.amount = request.amount
        db.commit()
    if request.type:
        if request.type == TransactionType.EXPENSE:
            wallet.amount -= 2 * transaction.amount
        elif request.type == TransactionType.INCOME:
            wallet.amount += 2 * transaction.amount
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
        transaction.type = request.type
        db.commit()
    if request.description:
        transaction.description = request.description
        db.commit()
    if request.date:
        transaction.date = datetime.strptime(request.date, "%Y-%m-%d %H:%M:%S")
        db.commit()
    if request.label:
        transaction.label = request.label
        db.commit()
    db.commit()
    return {"message": "Transaction updated successfully"}


@router.delete("/", dependencies=[Depends(validate_token)])
def delete_transaction(
    id: int, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    transaction = db.query(Transactions).filter(Transactions.id == id).first()
    if not transaction or transaction.user_id != user_info["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid request")
    wallet = db.query(Wallets).filter(Wallets.id == transaction.wallet_id).first()
    if transaction.type == TransactionType.EXPENSE:
        wallet.amount += transaction.amount
    elif transaction.type == TransactionType.INCOME:
        wallet.amount -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@router.post("/transfer")
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
