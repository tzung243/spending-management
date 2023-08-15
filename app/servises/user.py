from email.mime.text import MIMEText
import random
import re
import smtplib
import bcrypt
import string
from fastapi import HTTPException
from app.database import SessionLocal
from app.database.models import Users as DBUsers
from app.schema.user import UserCreate

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

# Configure email settings
conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_ADMIN,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_PORT = 587,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_SSL_TLS= False,
    MAIL_STARTTLS= True,
    MAIL_FROM = settings.MAIL_ADMIN
)


def is_valid_password(password, username=None):
    """
    Check if a password is valid.
    Return an error message if the password is invalid, or None if the password is valid.
    """
    # Check the length of the password
    if len(password) < 8 or len(password) > 64:
        return "Password must be between 8-64 characters long."

    # Check the security of the password
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$"
    if not re.match(pattern, password):
        return "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    # Check if the password contains personal information
    if username and username.lower() in password.lower():
        return "Password cannot contain your personal information."

    # Password is valid
    return None

def register_user(request: UserCreate, db: SessionLocal):
    db_user = db.query(DBUsers).filter(DBUsers.name == request.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    valid_password = is_valid_password(request.password, request.name)
    if valid_password is not None:
        raise HTTPException(status_code=400, detail=valid_password)
    token = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    # Adding the salt to password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), salt)
    user = DBUsers(name=request.name, email=request.email, password=hashed_password, token=token)
    db.add(user)
    db.commit()
    # response = send_verification_email(request.email, token)
    return "OK"

# def send_verification_email(email: str, token: str):
#     # msg = MIMEText(f"Please click the following link to verify your email: /verify/{email}/{token}")
#     # msg['Subject'] = "Email Verification"
#     # msg['From'] = settings.MAIL_ADMIN
#     # msg['To'] = email
#     # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
#     #    smtp_server.login( settings.MAIL_ADMIN, settings.MAIL_PASSWORD)
#     #    smtp_server.sendmail( settings.MAIL_ADMIN, email, msg.as_string())
#     # print("Message sent!")
#     message = MessageSchema(
#         subject="Email Verification",
#         recipients=[email],
#         body=f"Please click the following link to verify your email: /verify/{email}/{token}"
#     )
#     fm = FastMail(conf)
#     fm.send_message(message)
#     print(f"Verification email sent to: {email}")
