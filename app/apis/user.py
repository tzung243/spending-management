from datetime import datetime
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.servises.user import is_valid_password
from app.database import get_db
from app.database.models import Users as DBUsers
from app.schema.user import PasswordUpdate, UserCreate, UserLogin, UserUpdate
from app.security import generate_token
from app.security import get_user, validate_token

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/", dependencies=[Depends(validate_token)])
def get_user(
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(DBUsers).filter(DBUsers.id == user_info["user_id"]).first()
    if not db_user:
        return {"message": "User not found"}
    return {"user_name": db_user.name, "user_email": db_user.email}


@router.post("/register")
def register(
    request: UserCreate,
    db: Session = Depends(get_db),
):
    db_user = db.query(DBUsers).filter(DBUsers.name == request.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = db.query(DBUsers).filter(DBUsers.email == request.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    valid_password = is_valid_password(request.password, request.name)
    if valid_password is not None:
        raise HTTPException(status_code=400, detail=valid_password)
    # Adding the salt to password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), salt)
    user = DBUsers(name=request.name, email=request.email, password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}


@router.post("/login")
def signin(request: UserLogin, db: Session = Depends(get_db)):
    if request.name and request.email:
        raise HTTPException(status_code=401, detail="Invalid username or email")
    if not request.name and not request.email:
        raise HTTPException(status_code=401, detail="Missing username or email")
    user = None
    if request.name:
        user = db.query(DBUsers).filter(DBUsers.name == request.name).first()
    if request.email:
        user = db.query(DBUsers).filter(DBUsers.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not bcrypt.checkpw(
        request.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=422, detail="Invalid email or password")
    return {
        "message": "Success",
        "access_token": generate_token(user.name, user.id),
        "user": {"name": user.name, "email": user.email},
        "expires_in": 24 * 3,
        "token_created": datetime.now(),
    }


@router.delete("/data", dependencies=[Depends(validate_token)])
def delete_data_user(
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    query = """
        DELETE FROM wallets, labels, transactions, wallets_labels, activity_logs
        WHERE wallets.user_id = :user_id
    """
    db.execute(query, {"user_id": user_info["user_id"]})
    db.commit()
    return {"message": "Success"}


@router.put("/", dependencies=[Depends(validate_token)])
def update_user(
    request: UserUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    user = db.query(DBUsers).filter(DBUsers.name == user_info["user_name"]).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if request.name == user.name and request.email == user.email:
        raise HTTPException(status_code=400, detail="No changes")
    name_exited = (
        db.query(DBUsers)
        .filter(and_(DBUsers.name == request.name, DBUsers.id != user.id))
        .first()
    )
    if name_exited:
        raise HTTPException(status_code=400, detail="Username already exists")
    mail_exited = (
        db.query(DBUsers)
        .filter(and_(DBUsers.email == request.email, DBUsers.id != user.id))
        .first()
    )
    if mail_exited:
        raise HTTPException(status_code=400, detail="Email already exists")
    user.name = request.name
    user.email = request.email
    db.commit()
    return {"user": {"name": user.name, "email": user.email}}


@router.put("/password", dependencies=[Depends(validate_token)])
def change_password(
    request: PasswordUpdate,
    user_info: dict = Depends(get_user),
    db: Session = Depends(get_db),
):
    print(user_info)
    user = db.query(DBUsers).filter(DBUsers.name == user_info["user_name"]).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if not bcrypt.checkpw(
        request.old_password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=422, detail="password_mismatch")
    if request.old_password == request.new_password:
        raise HTTPException(status_code=422, detail="old_password")
    valid_password = is_valid_password(request.new_password, user.name)
    if valid_password is not None:
        raise HTTPException(status_code=400, detail=valid_password)
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.new_password.encode("utf-8"), salt)
    user.password = hashed_password
    db.commit()
    return {"message": "Password updated successfully"}
