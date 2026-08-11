from fastapi import FastAPI
from app.db import init_db
from app.routers import emails

app = FastAPI(title="Email Rendering and Sending API", version="1.0.1")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(emails.router)