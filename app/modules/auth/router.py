import logging

from fastapi import APIRouter, Depends, Form, Path
from fastapi.security import OAuth2PasswordRequestForm

from .service import AuthService
from .dependency import get_auth_service
from .schemas import SendOtpRequest, VerifyOtpRequest

from app.modules.users.models import User
from app.core.security import get_current_user
from app.services.task_service import get_task_status, TaskStatusResponse

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)


#---------------------------------------------
# User authentication using email and password
#---------------------------------------------
@router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends(), 
                auth_service: AuthService = Depends(get_auth_service)):
    logger.info(f"User with email: {request.username} is attempting to log in")
    return await auth_service.login(request.username, request.password)

@router.post("/refresh")
async def refresh_token(refresh_token: str = Form(...),
                        auth_service: AuthService = Depends(get_auth_service)):
    logger.info("Attempting to refresh access token")
    return await auth_service.refresh(refresh_token)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user),
                 auth_service: AuthService = Depends(get_auth_service)):
    logger.info(f"User {current_user.email} is attempting to log out")
    return await auth_service.logout(current_user.email)


#---------------------------------------
# Email verification and Email otp login
#---------------------------------------

@router.post("/send/otp")
async def send_otp(request: SendOtpRequest,
                   auth_service: AuthService = Depends(get_auth_service)):
    logger.info(f"Sending otp to email: {request.email}")
    return await auth_service.send_otp(request.email, request.request_type)

@router.post("/verify/otp")
async def verify_otp(request: VerifyOtpRequest,
                       auth_service: AuthService = Depends(get_auth_service)):
    logger.info(f"Verifying otp for email: {request.email}")
    return await auth_service.verify_otp(request.email, request.otp)

@router.post("/otp-login")
async def otp_login(request: VerifyOtpRequest,
                    auth_service: AuthService = Depends(get_auth_service)):
    logger.info(f"OTP login for email: {request.email}")
    return await auth_service.otp_login(request.email, request.otp)


#----------------------------
# Task Status Tracking
#----------------------------

@router.get("/task/status/{task_id}", response_model=TaskStatusResponse)
async def get_email_task_status(task_id: str = Path(..., description="The task ID to check status for")):
    """Get the status of an email task by task ID."""
    logger.info(f"Checking task status for: {task_id}")
    return get_task_status(task_id)