from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models import models
from app.db import database
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables asynchronously using the async engine before the app starts
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(title="DevSphere", lifespan=lifespan)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Welcome to DevSphere!"}
