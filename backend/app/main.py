"""
TriCare AI Backend Main Application

FastAPI application initialization with routes, middleware, and error handlers.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import uuid
from pathlib import Path
from datetime import datetime

from app.config import get_settings
from app.api.routes import health, reports, symptoms, imaging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create uploads directory if it doesn't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Medical triage and education web application with AI-powered features",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add unique correlation ID to each request for tracking."""
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    logger.info(
        f"Request started",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": get_remote_address(request)
        }
    )
    
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        f"Request completed",
        extra={
            "correlation_id": correlation_id,
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages and correlation ID."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.warning(
        f"Validation error",
        extra={
            "correlation_id": correlation_id,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data. Please check your input and try again.",
            "details": exc.errors(),
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.warning(
        f"Rate limit exceeded",
        extra={
            "correlation_id": correlation_id,
            "client_ip": get_remote_address(request),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully with detailed logging."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"correlation_id": correlation_id},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        }
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(symptoms.router, prefix="/api/symptoms", tags=["Symptoms"])
app.include_router(imaging.router, prefix="/api/imaging", tags=["Imaging"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Allowed origins: {settings.cors_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
