"""
API router registry.

This module exposes a small helper `register_router` used by the
application startup code to include all FastAPI routers (auth, profiles,
etc.) into the main FastAPI application instance.
"""

from fastapi import FastAPI
from app.auth.controller import router as auth_router
# from app.profiles.controller import router as profile_router


def register_router(app: FastAPI):
    """
    Register all application routers on the given FastAPI instance.
    """
    app.include_router(auth_router)
    # app.include_router(profile_router)
