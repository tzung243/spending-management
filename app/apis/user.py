import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.servises.user import is_valid_password
from app.database import get_db
from app.database.models import Users as DBUsers
from app.schema.user import UserCreate, UserLogin
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
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Success", "token": generate_token(user.name, user.id)}


@router.delete("/data", dependencies=[Depends(validate_token)])
def delere_data_user(
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
