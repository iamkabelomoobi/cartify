from sqlalchemy import Column, Integer, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    access_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=False)
    otp = Column(Integer, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship(
        "User",
        back_populates="sessions",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Session id={self.id} user_id={self.user_id!r} is_active={self.is_active!r}>"
