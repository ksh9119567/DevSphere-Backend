"""
This module contains event classes for blog events.
"""

from app.events.base import BaseEvent


class BlogCreatedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int, email: str):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        self.email = email
        
        
class BlogUpdatedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int, email: str):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        self.email = email


class BlogDeletedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int, email: str):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        self.email = email
        

class AllBlogDeletedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int, email: str):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        self.email = email
        

class BlogLikeEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        
        
class BlogUnLikeEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        
        
class BlogBookmarkEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id


class BlogUnBookmarkEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id