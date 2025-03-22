from fastapi import APIRouter

from app.api.routes import accounts, items, login, private, users, utils, broker_api
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(accounts.router)
api_router.include_router(broker_api.router)
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
