from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as doc_router
from app.api.routes.chat import router as chat_router

router = APIRouter(prefix="/api/v1")

router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

router.include_router(
    doc_router,
    prefix="/doc"
)

router.include_router(
    chat_router,
    prefix="/chat"
)