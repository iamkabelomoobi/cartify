from sqlalchemy import Column, String, DateTime, func
from app.core.database import Base


class OTP(Base):
    __tablename__ = "otps"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    used = Column(String, default="false", nullable=False)  # "true" or "false"

    def __repr__(self) -> str:
        return f"<OTP id={self.id} user_id={self.user_id} code={self.code!r} used={self.used}>"
