import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BlogBase, BlogResponse, BlogCreateResponse, BlogUpdateResponse
from .service import BlogService
from .dependency import get_blog_service

from app.modules.users.models import User
from app.db.database import get_db
from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_user, get_current_admin_user
from app.core.exception import PermissionDeniedException

router = APIRouter(prefix="/blogs", tags=["Blogs"])
logger = logging.getLogger(__name__)


@router.post("/create-blog", response_model=StandardResponse[BlogCreateResponse])
async def create_blog(request: BlogBase, 
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is creating a blog with title: {request.title}")
    response = await blog_service.create_blog(request, current_user.id)
    return success_response("Blog created successfully", response)

@router.get("/get-user-blogs", response_model=StandardResponse[list[BlogResponse]])
async def get_user_blogs(blog_service: BlogService = Depends(get_blog_service),
                         current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their blogs")
    response = await blog_service.get_user_blogs(current_user.id)
    return success_response("Blogs fetched successfully", response)

@router.get("/admin/get-user-blogs/{user_id}", response_model=StandardResponse[list[BlogResponse]])
async def get_user_blogs_by_id(user_id: uuid.UUID, 
                               blog_service: BlogService = Depends(get_blog_service),
                               admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching blogs for user_id: {user_id}")
    response = await blog_service.get_user_blogs(user_id)
    return success_response("Blogs fetched successfully", response)

@router.get("/get-blog/{blog_id}", response_model=StandardResponse[BlogResponse])
async def get_blog(blog_id: uuid.UUID, 
                   user_id: uuid.UUID = None, 
                   blog_service: BlogService = Depends(get_blog_service),
                   current_user: User = Depends(get_current_user)):
    if user_id and current_user.is_admin:
        logger.info(f"Admin {current_user.email} is fetching blog with id: {blog_id} belonging to user_id: {user_id}")
        response = await blog_service.get_blog(blog_id, user_id)
        return success_response("Blog fetched successfully", response)
    
    elif user_id and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted to access blog with id: {blog_id} belonging to user_id: {user_id}")
        raise PermissionDeniedException("Only admins can access other users' blogs")
    
    logger.info(f"User {current_user.email} is fetching blog with id: {blog_id}")
    response = await blog_service.get_blog(blog_id=blog_id, user_id=current_user.id)
    return success_response("Blog fetched successfully", response)

@router.get("/admin/get-blog/all", response_model=StandardResponse[list[BlogResponse]])
async def get_all_blog(blog_service: BlogService = Depends(get_blog_service),
                       admin_user: User = Depends(get_current_admin_user)):
    logger.info(f"Admin {admin_user.email} is fetching all blogs")
    response = await blog_service.get_all_blogs()
    return success_response("All blogs fetched successfully", response)

@router.put("/update-blog/{blog_id}", response_model=StandardResponse[BlogUpdateResponse])
async def update_blog(blog_id: uuid.UUID,
                      request: BlogBase,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating blog with id: {blog_id}")
    response = await blog_service.update_blog(blog_id, request, current_user.id, current_user.is_admin)
    return success_response("Blog updated successfully", response)

@router.delete("/delete-blog/{blog_id}")
async def delete_blog(blog_id: uuid.UUID,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting blog with id: {blog_id}")
    response = await blog_service.delete_blog(blog_id, current_user.id, current_user.is_admin)
    return success_response("Blogs deleted successfully", response)

@router.delete("/delete/all/")
async def delete_all_blogs(blog_service: BlogService = Depends(get_blog_service),
                           current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting all their blogs")
    response = await blog_service.delete_all_blogs(current_user.id)
    return success_response("All blogs deleted successfully", response)