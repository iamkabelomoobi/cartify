from __future__ import annotations

import logging
import uuid

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.schemas.user import User
from app.schemas.admin import Admin
from app.schemas.customer import Customer

logger = logging.getLogger("cartify.seeder")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_user_if_missing(
    db,
    email: str,
    password: str,
    role: str = "customer",
    is_verified: bool = False,
    phone: str | None = None,
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.info(f"User {email} already exists. Updating password hash...")
        # Update password to ensure it's properly hashed
        existing.password = hash_password(password)
        db.commit()
        return existing

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        phone=phone,
        password=hash_password(password),
        role=role,
        is_verified=is_verified,
    )
    db.add(user)
    db.flush()
    logger.info(f"Created user: {email}")
    return user


def create_admin_profile_if_missing(
    db, user: User, first_name: str = "Admin", last_name: str = "User"
):
    existing = db.query(Admin).filter(Admin.user_id == user.id).first()
    if existing:
        logger.info(f"Admin profile for {user.email} already exists.")
        return existing

    admin_id = str(uuid.uuid4())
    admin = Admin(
        id=admin_id,
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(admin)
    db.flush()
    logger.info(f"Created admin profile for {user.email}")
    return admin


def create_customer_profile_if_missing(
    db, user: User, first_name: str = "Sample", last_name: str = "Customer"
):
    existing = db.query(Customer).filter(Customer.user_id == user.id).first()
    if existing:
        logger.info(f"Customer profile for {user.email} already exists.")
        return existing

    customer_id = str(uuid.uuid4())
    customer = Customer(
        id=customer_id,
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(customer)
    db.flush()
    logger.info(f"Created customer profile for {user.email}")
    return customer


def seed():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        admin_user = create_user_if_missing(
            db,
            email="admin@example.com",
            password="adminpassword123",
            role="admin",
            is_verified=True,
        )
        create_admin_profile_if_missing(db, admin_user, "Admin", "User")

        customer_user = create_user_if_missing(
            db,
            email="customer@example.com",
            password="customerpassword123",
            role="customer",
            is_verified=True,
        )
        create_customer_profile_if_missing(db, customer_user, "John", "Doe")

        customer_user2 = create_user_if_missing(
            db,
            email="customer2@example.com",
            password="customerpassword123",
            role="customer",
            is_verified=False,
        )
        create_customer_profile_if_missing(db, customer_user2, "Jane", "Smith")

        db.commit()
        logger.info("✅ User seeding completed successfully!")

    except Exception as e:
        logger.exception("❌ Seeding failed: %s", e)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
