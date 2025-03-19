from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    course_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0
    dislikes: int = 0
    liked_by: list[str] = []  # 存储点赞用户的ID
    disliked_by: list[str] = []  # 存储踩的用户的ID