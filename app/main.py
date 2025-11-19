from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from sqlalchemy import text
from app.core.database import Base, engine
from app.core.redis import ping_redis
from app.routers import auth

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check database connection
    db_connected = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
        logger.info("Database connection successful.")
    except Exception as exc:
        logger.exception("Database connection failed during startup: %s", exc)

    app.state.db_connected = db_connected

    # Check Redis connection
    redis_connected = ping_redis()
    app.state.redis_connected = redis_connected

    yield

    logger.info("Shutting down Cartify API.")


# Ensure all ORM model modules are imported
try:
    import app.schemas.user  # noqa: F401
    import app.schemas.admin  # noqa: F401
    import app.schemas.customer  # noqa: F401
    import app.schemas.otp  # noqa: F401
except ImportError:
    logger.debug("One or more schema modules failed to import during startup.")


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cartify API",
    lifespan=lifespan,
)

app.include_router(auth.router)


@app.get("/")
def welcome():
    return {
        "message": "Welcome to Cartify",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "db_connected": getattr(app.state, "db_connected", False),
        "redis_connected": getattr(app.state, "redis_connected", False),
    }
