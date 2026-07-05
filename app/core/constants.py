from enum import Enum

class BlogStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"