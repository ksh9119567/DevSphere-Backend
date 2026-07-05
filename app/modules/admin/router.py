from fastapi import APIRouter
from .users import router as user_router
from .blogs import router as blog_router

router = APIRouter(prefix="/admin", tags=["Admin"])

router.include_router(user_router)
router.include_router(blog_router)