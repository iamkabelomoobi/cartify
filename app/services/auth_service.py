from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException, status
from app.schemas.user import User
from app.schemas.customer import Customer
from app.schemas.session import Session
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
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.core.security import AuthService as SecurityService
from app.utils.otp import (
    generate_otp,
    store_otp_redis,
    get_otp_redis,
    delete_otp_redis,
)
from app.utils.email import send_email
from app.templates.auth import (
    get_otp_email_template,
    get_welcome_email_template,
    get_password_reset_success_email_template,
)
from app.core.redis import get_redis
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger("uvicorn.error")


class AuthService:
    """Service class handling all authentication business logic"""

    def __init__(self, security_service: SecurityService | None = None):
        self.security = security_service or SecurityService()

    async def register_user(
        self, db: DBSession, data: RegisterRequest
    ) -> RegisterResponse:
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
        hashed_pwd = self.security.hash_password(data.password)
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

    def login_user(self, db: DBSession, data: LoginRequest) -> LoginResponse:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        try:
            is_password_valid = self.security.verify_password(
                data.password, user.password
            )

        except Exception as e:
            logger.error(f"Password verification error for {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not is_password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        existing_session = (
            db.query(Session)
            .filter(
                Session.user_id == user.id,
                Session.is_active == True,
                Session.refresh_token_expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

        if existing_session:
            if existing_session.access_token_expires_at > datetime.now(timezone.utc):
                return LoginResponse(
                    access_token=existing_session.access_token,
                    refresh_token=existing_session.refresh_token,
                )
            else:
                new_access_token = self.security.create_access_token(
                    data={"sub": user.id, "email": user.email, "role": user.role}
                )
                access_token_expiration = self.security.get_token_expiration(
                    new_access_token
                )

                existing_session.access_token = new_access_token
                existing_session.access_token_expires_at = access_token_expiration
                db.commit()

                return LoginResponse(
                    access_token=new_access_token,
                    refresh_token=existing_session.refresh_token,
                )

        db.query(Session).filter(Session.user_id == user.id).update(
            {"is_active": False}
        )
        db.commit()

        access_token = self.security.create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role}
        )
        refresh_token = self.security.create_refresh_token(
            data={"sub": user.id, "email": user.email, "role": user.role}
        )

        access_token_expiration = self.security.get_token_expiration(access_token)
        refresh_token_expiration = self.security.get_token_expiration(refresh_token)

        session_id = str(uuid.uuid4())
        new_session = Session(
            id=session_id,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            is_active=True,
            access_token_expires_at=access_token_expiration,
            refresh_token_expires_at=refresh_token_expiration,
        )
        db.add(new_session)
        db.commit()

        return LoginResponse(access_token=access_token, refresh_token=refresh_token)

    def logout_user(self, db: DBSession, access_token: str) -> LogoutResponse:
        payload = self.security.verify_token(access_token)
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

        session = (
            db.query(Session)
            .filter(Session.user_id == user_id, Session.access_token == access_token)
            .first()
        )

        if session:
            session.is_active = False
            db.commit()
            logger.info(f"User logged out: user_id={user_id}, session_id={session.id}")
        else:
            logger.warning(f"No active session found for user_id={user_id}")

        return LogoutResponse(message="Logged out successfully")

    def refresh_access_token(
        self, db: DBSession, data: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        payload = self.security.verify_token(data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        user_email = payload.get("email")
        user_role = payload.get("role")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        session = (
            db.query(Session)
            .filter(
                Session.refresh_token == data.refresh_token,
                Session.is_active == True,
            )
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive session",
            )

        current_time = datetime.now(timezone.utc)

        if session.refresh_token_expires_at <= current_time:
            session.is_active = False
            db.commit()
            logger.info(
                f"Refresh token expired for user_id={user_id}, session invalidated"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired, please login again",
            )

        new_access_token = self.security.create_access_token(
            data={"sub": user_id, "email": user_email, "role": user_role}
        )
        access_token_expiration = self.security.get_token_expiration(new_access_token)

        time_until_refresh_expiry = (
            session.refresh_token_expires_at - current_time
        ).total_seconds()
        refresh_token_threshold = 86400  # 1 day in seconds

        if time_until_refresh_expiry < refresh_token_threshold:
            new_refresh_token = self.security.create_refresh_token(
                data={"sub": user_id, "email": user_email, "role": user_role}
            )
            refresh_token_expiration = self.security.get_token_expiration(
                new_refresh_token
            )

            session.access_token = new_access_token
            session.refresh_token = new_refresh_token
            session.access_token_expires_at = access_token_expiration
            session.refresh_token_expires_at = refresh_token_expiration
            db.commit()

            return RefreshTokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )
        else:
            session.access_token = new_access_token
            session.access_token_expires_at = access_token_expiration
            db.commit()

            return RefreshTokenResponse(
                access_token=new_access_token,
                refresh_token=data.refresh_token,
            )

    async def forgot_password(
        self, db: DBSession, data: ForgotPasswordRequest
    ) -> ForgotPasswordResponse:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return ForgotPasswordResponse(
                message="If the email exists, an OTP has been sent"
            )

        otp_code = generate_otp()
        otp_verification_token = self.security.create_otp_verification_token(
            user.id, user.email
        )

        if not otp_code or not otp_verification_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate OTP",
            )

        redis_client = get_redis()
        store_otp_redis(redis_client, user.email, otp_code)

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

    def verify_otp(self, db: DBSession, data: VerifyOTPRequest) -> VerifyOTPResponse:
        payload = self.security.verify_otp_verification_token(
            data.otp_verification_token
        )
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

        reset_token = self.security.create_reset_token(user.id, user.email)

        return VerifyOTPResponse(
            message="OTP verified successfully", reset_token=reset_token
        )

    async def reset_password(
        self, db: DBSession, data: ResetPasswordRequest
    ) -> ResetPasswordResponse:
        payload = self.security.verify_reset_token(data.reset_token)
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

        if self.security.verify_password(data.new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as the old password",
            )

        user.password = self.security.hash_password(data.new_password)

        db.query(Session).filter(Session.user_id == user.id).update(
            {"is_active": False}
        )

        db.commit()

        reset_success_body = get_password_reset_success_email_template(user.email)
        await send_email(
            subject="Cartify - Password Reset Successful",
            recipients=[user.email],
            body=reset_success_body,
        )

        return ResetPasswordResponse(message="Password reset successfully")
