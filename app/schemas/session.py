from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    access_token = Column(String(512), unique=True, nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    access_token_expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship(
        "User",
        back_populates="sessions",
    )

    def __repr__(self) -> str:
        return (
            f"<Session id={self.id} "
            f"user_id={self.user_id!r} "
            f"is_active={self.is_active!r}>"
        )
