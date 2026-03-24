from pydantic import BaseModel, EmailStr


class SendOtpRequest(BaseModel):
    email: EmailStr
    request_type: str
    
class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    