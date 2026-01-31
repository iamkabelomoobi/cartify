from fastapi import APIRouter, Depends, Header, HTTPException, status
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
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.services.auth_service import AuthService


class AuthRouter:
    """Authentication router class handling all auth-related endpoints"""

    def __init__(self, auth_service: AuthService | None = None):
        """Initialize router with optional AuthService instance"""
        self.auth_service = auth_service or AuthService()
        self.router = APIRouter(prefix="/auth", tags=["Authentication"])
        self._register_routes()

    def _register_routes(self):
        """Register all authentication routes"""
        self.router.add_api_route(
            "/register",
            self.register,
            methods=["POST"],
            response_model=RegisterResponse,
            status_code=201,
            summary="Register a new user",
            description="Register a new user with customer profile",
        )

        self.router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=LoginResponse,
            summary="User login",
            description="Login with email and password",
        )

        self.router.add_api_route(
            "/logout",
            self.logout,
            methods=["POST"],
            response_model=LogoutResponse,
            summary="User logout",
            description="Logout user by invalidating session",
        )

        self.router.add_api_route(
            "/refresh",
            self.refresh_token,
            methods=["POST"],
            response_model=RefreshTokenResponse,
            summary="Refresh access token",
            description="Refresh access token using refresh token",
        )

        self.router.add_api_route(
            "/forgot-password",
            self.forgot_password,
            methods=["POST"],
            response_model=ForgotPasswordResponse,
            summary="Request password reset",
            description="Step 1: Request password reset OTP and receive verification token",
        )

        self.router.add_api_route(
            "/verify-otp",
            self.verify_otp,
            methods=["POST"],
            response_model=VerifyOTPResponse,
            summary="Verify OTP",
            description="Step 2: Verify OTP using verification token and get password reset token",
        )

        self.router.add_api_route(
            "/reset-password",
            self.reset_password,
            methods=["POST"],
            response_model=ResetPasswordResponse,
            summary="Reset password",
            description="Step 3: Reset password using reset token",
        )

    async def register(
        self, data: RegisterRequest, db: Session = Depends(get_db)
    ) -> RegisterResponse:
        """Register a new user with customer profile"""
        return await self.auth_service.register_user(db, data)

    def login(self, data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
        """Login with email and password"""
        return self.auth_service.login_user(db, data)

    def logout(
        self, authorization: str = Header(...), db: Session = Depends(get_db)
    ) -> LogoutResponse:
        """Logout user by invalidating session"""
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )

        access_token = authorization.replace("Bearer ", "")
        return self.auth_service.logout_user(db, access_token)

    def refresh_token(
        self, data: RefreshTokenRequest, db: Session = Depends(get_db)
    ) -> RefreshTokenResponse:
        """Refresh access token using refresh token"""
        return self.auth_service.refresh_access_token(db, data)

    async def forgot_password(
        self, data: ForgotPasswordRequest, db: Session = Depends(get_db)
    ) -> ForgotPasswordResponse:
        """Step 1: Request password reset OTP and receive verification token"""
        return await self.auth_service.forgot_password(db, data)

    def verify_otp(
        self, data: VerifyOTPRequest, db: Session = Depends(get_db)
    ) -> VerifyOTPResponse:
        """Step 2: Verify OTP using verification token and get password reset token"""
        return self.auth_service.verify_otp(db, data)

    async def reset_password(
        self, data: ResetPasswordRequest, db: Session = Depends(get_db)
    ) -> ResetPasswordResponse:
        """Step 3: Reset password using reset token"""
        return await self.auth_service.reset_password(db, data)


# Create router instance
auth_router = AuthRouter()
router = auth_router.router
