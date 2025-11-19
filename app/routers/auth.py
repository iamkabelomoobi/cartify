from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with customer profile"""
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    return auth_service.login_user(db, data)


@router.post("/logout", response_model=LogoutResponse)
def logout(authorization: str = Header(...)):
    """Logout user by invalidating tokens"""
    if not authorization.startswith("Bearer "):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    access_token = authorization.replace("Bearer ", "")
    return auth_service.logout_user(access_token)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Step 1: Request password reset OTP and receive verification token"""
    return await auth_service.forgot_password(db, data)


@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Step 2: Verify OTP using verification token and get password reset token"""
    return auth_service.verify_otp(db, data)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Step 3: Reset password using reset token"""
    return await auth_service.reset_password(db, data)
