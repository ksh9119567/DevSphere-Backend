import logging
import uuid

from fastapi import APIRouter, Depends

from .schemas import BlogCreate, BlogResponse, BlogListResponse, BlogUpdate
from .service import BlogService
from .dependency import get_blog_service

from app.modules.users.models import User
from app.core.schemas import StandardResponse
from app.core.response import success_response
from app.core.security import get_current_user

router = APIRouter(prefix="/blogs", tags=["Blogs"])
logger = logging.getLogger(__name__)


#---------------------------------------
# Blog Creation and management endpoints
#---------------------------------------
@router.post("/create/blog", response_model=StandardResponse[BlogResponse])
async def create_blog(request: BlogCreate, 
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is creating a blog with title: {request.title}")
    response = await blog_service.create_blog(request, current_user.id)
    return success_response("Blog created successfully", response["blog"])

@router.get("/get/blogs/user", response_model=StandardResponse[list[BlogListResponse]])
async def get_current_user_blogs(blog_service: BlogService = Depends(get_blog_service),
                                 current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching their blogs")
    response = await blog_service.get_user_blogs(current_user.id)
    return success_response("Blogs fetched successfully", response)

#both for admin and normal users
@router.get("/get/blogs/user/{user_id}", response_model=StandardResponse[list[BlogListResponse]])
async def get_user_blogs_by_id(user_id: uuid.UUID, 
                               blog_service: BlogService = Depends(get_blog_service),
                               current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is fetching blogs for user_id: {user_id}")
    response = await blog_service.get_user_blogs(user_id)
    return success_response("Blogs fetched successfully", response)

@router.get("/get/blog/{blog_id}", response_model=StandardResponse[BlogResponse])
async def get_blog(blog_id: uuid.UUID,
                   blog_service: BlogService = Depends(get_blog_service),
                   current_user: User = Depends(get_current_user)):    
    logger.info(f"User {current_user.email} is fetching blog with id: {blog_id}")
    response = await blog_service.get_blog(blog_id=blog_id)
    return success_response("Blog fetched successfully", response)

@router.put("/update/blog/{blog_id}", response_model=StandardResponse[BlogResponse])
async def update_blog(blog_id: uuid.UUID,
                      request: BlogUpdate,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is updating blog with id: {blog_id}")
    response = await blog_service.update_blog(blog_id, request, current_user.id, current_user.is_admin)
    return success_response("Blog updated successfully", response["blog"])

@router.delete("/delete/blog/{blog_id}")
async def delete_blog(blog_id: uuid.UUID,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting blog with id: {blog_id}")
    response = await blog_service.delete_blog(blog_id, current_user.id, current_user.is_admin)
    return success_response("Blogs deleted successfully", response)

@router.delete("/delete/blogs/user/all/")
async def delete_all_blogs(blog_service: BlogService = Depends(get_blog_service),
                           current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is deleting all their blogs")
    response = await blog_service.delete_all_blogs(current_user.id)
    return success_response("All blogs deleted successfully", response)

#-------------------------------------------------------------
# Blog engagement endpoints (like/unlike, bookmark/unbookmark)
#-------------------------------------------------------------
@router.post("/like/blog/{blog_id}")
async def like_blog(blog_id: uuid.UUID,
                    blog_service: BlogService = Depends(get_blog_service),
                    current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is liking blog with id: {blog_id}")
    response = await blog_service.like_blog(blog_id, current_user.id)
    return success_response("Blog liked successfully", response)

@router.delete("/unlike/blog/{blog_id}")
async def unlike_blog(blog_id: uuid.UUID,
                      blog_service: BlogService = Depends(get_blog_service),
                      current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is unliking blog with id: {blog_id}")
    response = await blog_service.unlike_blog(blog_id, current_user.id)
    return success_response("Blog unliked successfully", response)

@router.post("/bookmark/blog/{blog_id}")
async def bookmark_blog(blog_id: uuid.UUID, 
                        blog_service: BlogService = Depends(get_blog_service),
                        current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is bookmarking blog with id: {blog_id}")
    response = await blog_service.bookmark_blog(blog_id, current_user.id)
    return success_response("Blog bookmarked successfully", response)

@router.delete("/unbookmark/blog/{blog_id}")
async def unbookmark_blog(blog_id: uuid.UUID,
                          blog_service: BlogService = Depends(get_blog_service),
                          current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.email} is unbookmarking blog with id: {blog_id}")
    response = await blog_service.unbookmark_blog(blog_id, current_user.id)
    return success_response("Blog unbookmarked successfully", response)