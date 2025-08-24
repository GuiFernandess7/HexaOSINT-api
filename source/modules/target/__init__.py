from fastapi import APIRouter

target_router = APIRouter(prefix="/target", tags=["target"])

from .routes import target_routes
