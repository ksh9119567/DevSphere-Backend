import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.api.router import router as api_router
from app.core.exception import (
    DevsphereException, NotFoundException, ValidationException,
    AuthenticationException, PermissionDeniedException
)
from app.core.middleware import ActivityTrackingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables asynchronously using the async engine before the app starts
    logger.info("Starting DevSphere application")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    yield
    logger.info("Shutting down DevSphere application")


app = FastAPI(title="DevSphere", lifespan=lifespan)

# Add activity tracking middleware
app.add_middleware(ActivityTrackingMiddleware)

# Exception handlers
@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    logger.warning(f"Not found error: {str(exc)} for path {request.url.path}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    logger.warning(f"Validation error: {str(exc)} for path {request.url.path}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(AuthenticationException)
async def auth_handler(request: Request, exc: AuthenticationException):
    logger.warning(f"Authentication error: {str(exc)} for path {request.url.path}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(PermissionDeniedException)
async def permission_handler(request: Request, exc: PermissionDeniedException):
    logger.warning(f"Permission denied: {str(exc)} for path {request.url.path}")
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(DevsphereException)
async def devsphere_handler(request: Request, exc: DevsphereException):
    logger.error(f"DevSphere error: {str(exc)} for path {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to DevSphere!"}
