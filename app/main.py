from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from sqlalchemy import text
from app.core.database import Base, engine


logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connected = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        connected = True
        logger.info("Database connection successful.")
    except Exception as exc:
        logger.exception("Database connection failed during startup: %s", exc)

    app.state.db_connected = connected

    yield

    logger.info("Shutting down Cartify API.")


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cartify API",
    lifespan=lifespan,
)


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
    }
