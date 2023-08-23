from fastapi import Depends, FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app = FastAPI()

from app.apis import user, wallet, transaction_label, transaction, analytics

app.include_router(user.router)
app.include_router(wallet.router)
app.include_router(transaction_label.router)
app.include_router(transaction.router)
app.include_router(analytics.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to my app"}
