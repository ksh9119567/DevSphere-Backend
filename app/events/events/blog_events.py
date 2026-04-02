from app.events.base import BaseEvent


class BlogCreatedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        
        
class BlogUpdatedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id


class BlogDeletedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id
        

class AllBlogDeletedEvent(BaseEvent):
    def __init__(self, blog_id: int, user_id: int):
        super().__init__()
        self.blog_id = blog_id
        self.user_id = user_id