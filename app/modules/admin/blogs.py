import logging
import uuid

from fastapi import APIRouter, Depends

from app.modules.blogs.schemas import BlogCreate, BlogAdminResponse, BlogListResponse, BlogAdminUpdate
from app.modules.blogs.service import BlogService
from app.modules.blogs.dependency import get_blog_service

from app.modules.users.models import User   
from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_admin_user

router = APIRouter(prefix="/blogs")
logger = logging.getLogger(__name__)

@router.post("/create/blog/{user_id}", response_model=StandardResponse[BlogAdminResponse])
async def create_blog(user_id: uuid.UUID,
                      request: BlogCreate, 
                      blog_service: BlogService = Depends(get_blog_service),
                      admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"User {admin_user.email} is creating a blog with title: {request.title}")
    response = await blog_service.create_blog(request, user_id)
    return success_response("Blog created successfully", response["blog"])

@router.get("/get/blog/all", response_model=StandardResponse[list[BlogListResponse]])
async def get_all_blog(blog_service: BlogService = Depends(get_blog_service),
                       admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is fetching all blogs")
    response = await blog_service.get_all_blogs()
    return success_response("All blogs fetched successfully", response)

@router.get("/get/blog/{blog_id}", response_model=StandardResponse[BlogAdminResponse])
async def get_blog(blog_id: uuid.UUID,
                   blog_service: BlogService = Depends(get_blog_service),
                   admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"User {admin_user.email} is fetching blog with id: {blog_id}")
    response = await blog_service.get_blog(blog_id=blog_id)
    return success_response("Blog fetched successfully", response)

@router.put("/update/blog/{blog_id}", response_model=StandardResponse[BlogAdminResponse])
async def update_blog(blog_id: uuid.UUID,
                      request: BlogAdminUpdate,
                      blog_service: BlogService = Depends(get_blog_service),
                      admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"User {admin_user.email} is updating blog with id: {blog_id}")
    response = await blog_service.update_blog(blog_id, request, admin_user.id, admin_user.is_admin)
    return success_response("Blog updated successfully", response["blog"])

@router.delete("/delete/blogs/user/all/{user_id}")
async def delete_user_blogs(user_id: uuid.UUID,
                            blog_service: BlogService = Depends(get_blog_service),
                            admin_user: User = Depends(get_current_admin_user)):
    
    logger.info(f"Admin {admin_user.email} is deleting all blogs for user_id: {user_id}")
    await blog_service.delete_all_blogs(user_id)
    return success_response("All blogs for user deleted successfully")

