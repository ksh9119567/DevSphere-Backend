from fastapi import APIRouter

from app.modules.blogs.router import router as blog_router
from app.modules.users.router import router as user_router
from app.modules.auth.router import router as auth_router
from app.modules.activity.router import router as activity_router
from app.modules.admin.router import router as admin_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(user_router)
router.include_router(blog_router)
router.include_router(activity_router)