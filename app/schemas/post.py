from datetime import datetime
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.user import UserResponseForPost
from app.schemas.base import CommonQueryParams



class PostBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(...)
    note: Optional[str] = Field(None)
    media_path: Optional[str] = Field(None, max_length=500)


class PostCreate(PostBase):
    user_id: int = Field(..., gt=0)


class PostUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None)
    note: Optional[str] = Field(None)
    media_path: Optional[str] = Field(None, max_length=500)


class PostResponse(PostBase):
    id: int
    # user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponseForPost] = None

class PostQueryParams(CommonQueryParams):
    user_id: Optional[int] = Field(None, gt=0)
