from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_

from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models import Wallets as DBWallets
from app.schema.wallet import WalletCreate, WalletUpdate
from app.security import get_user, validate_token

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/all", dependencies=[Depends(validate_token)])
def get_all_wallets(user_info: dict = Depends(get_user), db: Session = Depends(get_db)):
    wallets = (
        db.query(DBWallets).filter(DBWallets.user_id == user_info["user_id"]).all()
    )
    if wallets is None:
        return []
    return wallets


@router.post("/", dependencies=[Depends(validate_token)])
def create_wallet(
    request: WalletCreate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    walletdb = (
        db.query(DBWallets)
        .filter(
            and_(
                DBWallets.name == request.name,
                DBWallets.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if walletdb:
        raise HTTPException(status_code=400, detail="Wallet name already exists")

    wallet = DBWallets(
        name=request.name,
        user_id=user_info["user_id"],
        type=request.type,
        amount=request.amount,
    )
    db.add(wallet)
    db.commit()

    return {wallet.name}


@router.put("/", dependencies=[Depends(validate_token)])
def update_wallet(
    request: WalletUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(DBWallets)
        .filter(
            and_(DBWallets.id == request.id, DBWallets.user_id == user_info["user_id"])
        )
        .first()
    )
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    if request.name:
        check_name = (
            db.query(DBWallets)
            .filter(
                DBWallets.name == request.name
                and DBWallets.user_id == user_info["user_id"]
            )
            .first()
        )
        if check_name:
            raise HTTPException(status_code=400, detail="Wallet name already exists")
        wallet.name = request.name
    if request.type:
        wallet.type = request.type
    if request.amount:
        wallet.amount = request.amount
    db.commit()
    return {"message": "Wallet updated successfully"}


@router.delete("/{wallet_id}", dependencies=[Depends(validate_token)])
def delete_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
):
    db.query(DBWallets).filter(DBWallets.id == wallet_id).delete()
    db.commit()
    return {"message": "Wallet deleted successfully"}


@router.get("/{wallet_id}", dependencies=[Depends(validate_token)])
def get_info_wallet(
    wallet_id: int, user_info: dict = Depends(get_user), db: Session = Depends(get_db)
):
    wallet = (
        db.query(DBWallets)
        .filter(
            and_(
                DBWallets.id == wallet_id and DBWallets.user_id == user_info["user_id"]
            )
        )
        .first()
    )
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    return wallet


@router.put("/{wallet_id}", dependencies=[Depends(validate_token)])
def update_wallet(
    wallet_id: int,
    body: WalletUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    wallet = (
        db.query(DBWallets)
        .filter(
            and_(
                DBWallets.id == wallet_id,
                DBWallets.user_id == user_info["user_id"],
            )
        )
        .first()
    )
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    if (
        body.name == wallet.name
        and body.type == wallet.type
        and body.amount == wallet.amount
    ):
        raise HTTPException(status_code=400, detail="No changes")

    if body.name != wallet.name:
        if body.name:
            check_name = (
                db.query(DBWallets)
                .filter(
                    DBWallets.name == body.name
                    and DBWallets.user_id == user_info["user_id"]
                )
                .first()
            )
            if check_name:
                raise HTTPException(
                    status_code=400, detail="Wallet name already exists"
                )

    wallet.name = body.name
    wallet.type = body.type
    wallet.amount = body.amount
    db.commit()
    return {"message": "Wallet updated successfully"}
