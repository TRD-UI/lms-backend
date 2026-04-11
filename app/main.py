"""
Application entrypoint and middleware configuration.

This module builds and configures the FastAPI application instance used by the
project. It sets up logging, middleware (CORS, session, rate limiting), mounts
routers and defines global exception handlers used across endpoints.
"""
from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.limiter.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi.errors import RateLimitExceeded
from app.api import register_router
from app.log import configure_logging, LogLevels
from app.config import settings

configure_logging(LogLevels.info)
app = FastAPI()


# adding slowapi middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware,
                   allow_origins=settings.ALLOWED_ORIGINS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY
)

register_router(app)


# custom rate_limiting exception.
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle requests that exceed configured rate limits.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded, try again after 1 minute."},
    )


@app.get("/", name="home")
async def root():
    """Return a small welcome payload used for health checks."""
    return {"message": "Welcome to TRD's LMS!"}
