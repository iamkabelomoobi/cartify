from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)


class RegisterResponse(BaseModel):
    message: str
    user_id: str
    email: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    otp_verification_token: str | None = None


class VerifyOTPRequest(BaseModel):
    otp_verification_token: str
    otp: str = Field(..., min_length=6, max_length=6)


class VerifyOTPResponse(BaseModel):
    message: str
    reset_token: str


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)


class ResetPasswordResponse(BaseModel):
    message: str
