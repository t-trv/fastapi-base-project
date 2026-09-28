from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.schemas.post import (
    PostCreate,
    BulkPostCreate,
    BulkPostDelete,
    PostUpdate,
    PostResponse,
    PostQueryParams,
)
from app.schemas.base import DataListResponse, PaginationMeta
from app.services import post as post_service

router = APIRouter()


@router.get("", response_model=DataListResponse[PostResponse])
async def list_posts(
    params: PostQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    queries = params.build_queries()
    items, total, _, _ = await post_service.get_posts_list(db, **queries)
    meta = PaginationMeta(
        total=total,
        offset=queries.get("offset", 0),
        limit=queries.get("limit", 10),
    )
    return DataListResponse(items=items, meta=meta)


@router.post("/bulk", response_model=list[PostResponse], status_code=201)
async def create_posts_bulk(
    payload: BulkPostCreate, db: AsyncSession = Depends(get_db)
):
    db_posts = await post_service.create_posts_bulk(db, payload.items)
    await db.commit()
    return db_posts


@router.delete("/bulk", response_model=list[PostResponse])
async def delete_posts_bulk(
    payload: BulkPostDelete, db: AsyncSession = Depends(get_db)
):
    db_posts = await post_service.delete_posts_bulk(db, payload.ids)
    await db.commit()
    return db_posts


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(post_in: PostCreate, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.create_post(db, post_in)
    await db.commit()
    return db_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await post_service.get_post_by_id(db, post_id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, post_in: PostUpdate, db: AsyncSession = Depends(get_db)
):
    db_post = await post_service.update_post(db, post_id, post_in)
    await db.commit()
    return db_post


@router.delete("/{post_id}", response_model=PostResponse)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post = await post_service.delete_post(db, post_id)
    await db.commit()
    return db_post
