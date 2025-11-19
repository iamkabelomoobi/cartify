from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import User
from app.schemas.customer import Customer
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
from app.core.security import (
    create_otp_verification_token,
    verify_otp_verification_token,
    create_refresh_token,
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    verify_reset_token,
    verify_token,
)
from app.utils.otp import (
    generate_otp,
    store_otp_redis,
    get_otp_redis,
    delete_otp_redis,
)
from app.utils.token_storage import (
    store_tokens_redis,
    get_tokens_redis,
    delete_tokens_redis,
)
from app.utils.email import send_email
from app.templates.auth import (
    get_otp_email_template,
    get_welcome_email_template,
    get_password_reset_success_email_template,
)
from app.core.redis import get_redis
import logging
import uuid

logger = logging.getLogger("uvicorn.error")


async def register_user(db: Session, data: RegisterRequest) -> RegisterResponse:
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if data.phone:
        existing_phone = db.query(User).filter(User.phone == data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(data.password)
    new_user = User(
        id=user_id,
        email=data.email,
        phone=data.phone,
        password=hashed_pwd,
        role="customer",
        is_verified=False,
    )
    db.add(new_user)
    db.flush()

    customer_id = str(uuid.uuid4())
    new_customer = Customer(
        id=customer_id,
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered: {new_user.email}")

    user_name = f"{data.first_name} {data.last_name}"
    welcome_body = get_welcome_email_template(user_name, new_user.email)
    await send_email(
        subject="Welcome to Cartify! 🛒",
        recipients=[new_user.email],
        body=welcome_body,
    )

    return RegisterResponse(
        message="User registered successfully",
        user_id=new_user.id,
        email=new_user.email,
        first_name=data.first_name,
        last_name=data.last_name,
    )


def login_user(db: Session, data: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.password or not user.password.startswith(("$2a$", "$2b$", "$2y$")):
        logger.error(f"User {user.email} has invalid password hash")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    redis_client = get_redis()

    existing_tokens = get_tokens_redis(redis_client, user.id)

    if (
        existing_tokens
        and "access_token" in existing_tokens
        and "refresh_token" in existing_tokens
    ):
        logger.info(f"User logged in with existing tokens: {user.email}")
        return LoginResponse(
            access_token=existing_tokens["access_token"],
            refresh_token=existing_tokens["refresh_token"],
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email, "role": user.role}
    )

    store_tokens_redis(redis_client, user.id, access_token, refresh_token)

    logger.info(f"User logged in with new tokens: {user.email}")

    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


def logout_user(access_token: str) -> LogoutResponse:
    """Logout user by invalidating tokens in Redis"""
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    redis_client = get_redis()
    delete_tokens_redis(redis_client, user_id)

    logger.info(f"User logged out: user_id={user_id}")

    return LogoutResponse(message="Logged out successfully")


async def forgot_password(
    db: Session, data: ForgotPasswordRequest
) -> ForgotPasswordResponse:
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return ForgotPasswordResponse(
            message="If the email exists, an OTP has been sent"
        )

    otp_code = generate_otp()
    otp_verification_token = create_otp_verification_token(user.id, user.email)

    if not otp_code or not otp_verification_token:
        logger.error(f"Failed to generate OTP or token for {user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OTP",
        )

    redis_client = get_redis()
    store_otp_redis(redis_client, user.email, user.id, otp_code)

    logger.info(f"OTP generated for {user.email}: {otp_code}")

    otp_body = get_otp_email_template(otp_code, user.email)
    await send_email(
        subject="Cartify - Password Reset OTP",
        recipients=[user.email],
        body=otp_body,
    )

    return ForgotPasswordResponse(
        message="If the email exists, an OTP has been sent",
        otp_verification_token=otp_verification_token,
    )


def verify_otp(db: Session, data: VerifyOTPRequest) -> VerifyOTPResponse:
    """Step 2: Verify OTP using the verification token and return a reset token"""
    payload = verify_otp_verification_token(data.otp_verification_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    redis_client = get_redis()
    otp_data = get_otp_redis(redis_client, user.email)

    if not otp_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    if otp_data["code"] != data.otp or otp_data["user_id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )

    delete_otp_redis(redis_client, user.email)

    reset_token = create_reset_token(user.id, user.email)

    logger.info(f"OTP verified for {user.email}, reset token issued")

    return VerifyOTPResponse(
        message="OTP verified successfully", reset_token=reset_token
    )


async def reset_password(
    db: Session, data: ResetPasswordRequest
) -> ResetPasswordResponse:
    """Step 3: Reset password using reset token and send confirmation email"""
    payload = verify_reset_token(data.reset_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if verify_password(data.new_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the old password",
        )

    user.password = hash_password(data.new_password)
    db.commit()

    logger.info(f"Password reset successful for {user.email}")

    reset_success_body = get_password_reset_success_email_template(user.email)
    await send_email(
        subject="Cartify - Password Reset Successful",
        recipients=[user.email],
        body=reset_success_body,
    )

    return ResetPasswordResponse(message="Password reset successfully")
