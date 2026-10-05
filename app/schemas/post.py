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


class BulkPostCreate(BaseSchema):
    items: list[PostCreate] = Field(..., min_length=1, max_length=1000)


class BulkPostDelete(BaseSchema):
    ids: list[int] = Field(..., min_length=1, max_length=1000)


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
    owner: Optional[UserResponseForPost] = Field(None, validation_alias="user")

class TrashedPostResponse(PostResponse):
    deleted_at: datetime

class PostQueryParams(CommonQueryParams):
    username: Optional[str] = Field(None)
