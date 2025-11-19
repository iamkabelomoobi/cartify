from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), unique=True, nullable=True)
    role = Column(String(50), nullable=False, default="customer")
    password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    admin = relationship(
        "Admin",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    customer = relationship(
        "Customer",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
