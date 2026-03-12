import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BlogBase, BlogResponse
from .service import BlogService

from app.modules.users.models import User
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.core.exception import PermissionDeniedException

router = APIRouter(prefix="/blogs", tags=["Blogs"])
logger = logging.getLogger(__name__)


@router.post("/create-blog", response_model=BlogResponse)
async def create_blog(request: BlogBase, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is creating a blog with title: {request.title}")
    return await BlogService.create_blog(request, current_user.id, db)

@router.get("/get-user-blogs", response_model=list[BlogResponse])
async def get_user_blogs(db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their blogs")
    return await BlogService.get_user_blogs(current_user.id, db)

@router.get("/admin/get-user-blogs/{user_id}", response_model=list[BlogResponse])
async def get_user_blogs_by_id(user_id: uuid.UUID, 
                               db: AsyncSession = Depends(get_db), 
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching blogs for user_id: {user_id}")
    return await BlogService.get_user_blogs(user_id, db)

@router.get("/get-blog/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: uuid.UUID, 
                   user_id: uuid.UUID, 
                   db: AsyncSession = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching blog with id: {blog_id} belonging to user_id: {user_id}")
        return await BlogService.get_blog(blog_id, user_id, db)
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access blog with id: {blog_id} belonging to user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' blogs")
    
    logger.info(f"User {current_user.email} is fetching blog with id: {blog_id}")
    return await BlogService.get_blog(blog_id=blog_id, user_id=current_user.id, db=db)

@router.get("/admin/get-blog/all", response_model=list[BlogResponse])
async def get_all_blog(db: AsyncSession = Depends(get_db),
                       admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all blogs")
    return await BlogService.get_all_blogs(db)

@router.put("/update-blog/{blog_id}", response_model=BlogResponse)
async def update_blog(blog_id: uuid.UUID,
                      request: BlogBase,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating blog with id: {blog_id}")
    return await BlogService.update_blog(blog_id, request, current_user.id, current_user.is_admin, db)

@router.delete("/delete-blog/{blog_id}")
async def delete_blog(blog_id: uuid.UUID,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting blog with id: {blog_id}")
    return await BlogService.delete_blog(blog_id, current_user.id, current_user.is_admin, db)
