from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    user = relationship("User", back_populates="admin")

    def __repr__(self) -> str:
        return f"<Admin id={self.id} user_id={self.user_id} name={self.first_name!r} {self.last_name!r}>"
