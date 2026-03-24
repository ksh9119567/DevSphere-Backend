import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BlogBase, BlogResponse
from .service import BlogService
from .dependency import get_blog_service

from app.modules.users.models import User
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.core.exception import PermissionDeniedException

router = APIRouter(prefix="/blogs", tags=["Blogs"])
logger = logging.getLogger(__name__)


def convert_blog_to_dict(blog) -> dict:
    """Convert Blog ORM object or cached dictionary to dictionary for Pydantic serialization.
    
    Handles both:
    - Blog ORM objects (from database)
    - Dictionaries (from Redis cache)
    """
    # If already a dictionary (from cache), return as-is
    if isinstance(blog, dict):
        return blog
    
    # Convert Blog ORM object to dictionary
    return {
        'id': str(blog.id),
        'user_id': str(blog.user_id),
        'title': blog.title,
        'content': blog.content,
        'created_at': blog.created_at.isoformat() if hasattr(blog.created_at, 'isoformat') else blog.created_at,
        'updated_at': blog.updated_at.isoformat() if hasattr(blog.updated_at, 'isoformat') else blog.updated_at,
    }


@router.post("/create-blog", response_model=BlogResponse)
async def create_blog(request: BlogBase, 
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is creating a blog with title: {request.title}")
    response = await blog_service.create_blog(request, current_user.id)
    return BlogResponse.model_validate(convert_blog_to_dict(response["data"]))

@router.get("/get-user-blogs", response_model=list[BlogResponse])
async def get_user_blogs(blog_service: BlogService = Depends(get_blog_service),
                         current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their blogs")
    response = await blog_service.get_user_blogs(current_user.id)
    return [BlogResponse.model_validate(convert_blog_to_dict(blog)) for blog in response["data"]]

@router.get("/admin/get-user-blogs/{user_id}", response_model=list[BlogResponse])
async def get_user_blogs_by_id(user_id: uuid.UUID, 
                               blog_service: BlogService = Depends(get_blog_service),
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching blogs for user_id: {user_id}")
    response = await blog_service.get_user_blogs(user_id)
    return [BlogResponse.model_validate(convert_blog_to_dict(blog)) for blog in response["data"]]

@router.get("/get-blog/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: uuid.UUID, 
                   user_id: uuid.UUID = None, 
                   blog_service: BlogService = Depends(get_blog_service),
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching blog with id: {blog_id} belonging to user_id: {user_id}")
        response = await blog_service.get_blog(blog_id, user_id)
        return BlogResponse.model_validate(convert_blog_to_dict(response["data"]))
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access blog with id: {blog_id} belonging to user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' blogs")
    
    logger.info(f"User {current_user.email} is fetching blog with id: {blog_id}")
    response = await blog_service.get_blog(blog_id=blog_id, user_id=current_user.id)
    return BlogResponse.model_validate(convert_blog_to_dict(response["data"]))

@router.get("/admin/get-blog/all", response_model=list[BlogResponse])
async def get_all_blog(blog_service: BlogService = Depends(get_blog_service),
                       admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all blogs")
    response = await blog_service.get_all_blogs()
    return [BlogResponse.model_validate(convert_blog_to_dict(blog)) for blog in response["data"]]

@router.put("/update-blog/{blog_id}", response_model=BlogResponse)
async def update_blog(blog_id: uuid.UUID,
                      request: BlogBase,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating blog with id: {blog_id}")
    response = await blog_service.update_blog(blog_id, request, current_user.id, current_user.is_admin)
    return BlogResponse.model_validate(convert_blog_to_dict(response["data"]))

@router.delete("/delete-blog/{blog_id}")
async def delete_blog(blog_id: uuid.UUID,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting blog with id: {blog_id}")
    return await blog_service.delete_blog(blog_id, current_user.id, current_user.is_admin)
