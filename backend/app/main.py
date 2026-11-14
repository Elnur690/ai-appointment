import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import setup_exception_handlers
from app.core.redis import init_redis, close_redis
from app.api.v1.router import api_v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "prod" and "dev-secret-key" in settings.SECRET_KEY:
        logger.warning("CRITICAL SECURITY WARNING: Replace SECRET_KEY in .env before running in production!")
    await init_db()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title="Randevu.vip — AI Appointment SaaS",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "prod" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "prod" else None,
)

# CORS configuration
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENVIRONMENT == "prod":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Exception handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_v1_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "domain": settings.PLATFORM_DOMAIN,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"])
@app.get("/api", tags=["System"])
@app.get("/api/v1", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "status": "online",
        "app": "Randevu.vip — AI Appointment SaaS API",
        "domain": settings.PLATFORM_DOMAIN,
        "version": "1.0.0",
    }
