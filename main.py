from fastapi import Depends, FastAPI, Request

from app.core.config import settings

app = FastAPI()

from app.apis import user, wallet, transaction_label, transaction, statics_user

app.include_router(user.router)
app.include_router(wallet.router)
app.include_router(transaction_label.router)
app.include_router(transaction.router)
app.include_router(statics_user.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my app"}
