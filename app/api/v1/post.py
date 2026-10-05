from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db

from app.schemas.base import CommonQueryParams, DataListResponse, PaginationMeta
from app.schemas.post import BulkPostCreate, BulkPostDelete, PostCreate, PostQueryParams, PostResponse, PostUpdate, TrashedPostResponse

from app.services import post as post_service

from app.utils.cache import cached, invalidate_cache
from app.utils.rate_limit import rate_limit

router = APIRouter()


@router.get("", response_model=DataListResponse[PostResponse])
@cached(expire=60, prefix="posts:list")
async def list_posts(
    params: PostQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    items, total, _, _ = await post_service.get_posts_list(
        db,
        search=params.search,
        username=params.username,
        offset=params.offset or 0,
        limit=params.limit or 10,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
    )
    meta = PaginationMeta(total=total, offset=params.offset or 0, limit=params.limit or 10)
    post_responses = [PostResponse.model_validate(item) for item in items]
    return DataListResponse[PostResponse](items=post_responses, meta=meta)


# Thùng rác phải đặt trước /{post_id} để không bị capture bởi path param\
@router.get("/trash", response_model=DataListResponse[TrashedPostResponse])
@cached(expire=60, prefix="posts:trash")
async def list_trashed_posts(
    params: CommonQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    items, total, _, _ = await post_service.get_trashed_posts(
        db,
        offset=params.offset or 0,
        limit=params.limit or 10,
        sort_order=params.sort_order,
    )
    meta = PaginationMeta(total=total, offset=params.offset or 0, limit=params.limit or 10)
    return DataListResponse[TrashedPostResponse](items=[TrashedPostResponse.model_validate(i) for i in items], meta=meta)


@router.post("/bulk", response_model=list[PostResponse], status_code=201)
@invalidate_cache(patterns=["posts:list:*"])
async def create_posts_bulk(payload: BulkPostCreate, db: AsyncSession = Depends(get_db)):
    db_posts = await post_service.create_posts_bulk(db, payload.items)
    await db.commit()
    return db_posts


@router.delete("/bulk", response_model=list[PostResponse])
@invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
async def delete_posts_bulk(payload: BulkPostDelete, db: AsyncSession = Depends(get_db)):
    db_posts = await post_service.delete_posts_bulk(db, payload.ids)
    await db.commit()
    return db_posts


@router.post("", response_model=PostResponse, status_code=201)
@rate_limit(limit=3, window=10, prefix="posts:create")
@invalidate_cache(patterns=["posts:list:*"])
async def create_post(post_in: PostCreate, request: Request, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.create_post(db, post_in)
    await db.commit()
    return db_post


@router.get("/{post_id}", response_model=PostResponse)
@cached(expire=120, prefix="posts:detail")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await post_service.get_post_by_id(db, post_id)


@router.put("/{post_id}", response_model=PostResponse)
@invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
async def update_post(post_id: int, post_in: PostUpdate, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.update_post(db, post_id, post_in)
    await db.commit()
    return db_post


# DELETE mềm -> vào thùng rác (deleted_at = now)
@router.delete("/{post_id}", response_model=PostResponse)
@invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.delete_post(db, post_id)
    await db.commit()
    return db_post


@router.post("/{post_id}/restore", response_model=PostResponse)
@invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
async def restore_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.restore_post(db, post_id)
    await db.commit()
    return db_post


@router.delete("/{post_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
@invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
async def hard_delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    await post_service.hard_delete_post(db, post_id)
    await db.commit()
    return None
