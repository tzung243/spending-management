from fastapi import FastAPI

from app.core.config import settings


app = FastAPI()

from app.apis import user

app.include_router(user.router)


@app.get("/")
async def root():
    return "Hello World"
