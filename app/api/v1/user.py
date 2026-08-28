from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.base import DataListResponse, PaginationMeta, CommonQueryParams
from app.services import user as user_service

router = APIRouter()


@router.get("", response_model=DataListResponse[UserResponse])
async def list_users(
    params: CommonQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    queries = params.build_queries()
    items, total, _, _ = await user_service.get_users_list(db, **queries)
    meta = PaginationMeta(
        total=total,
        offset=queries.get("offset", 0),
        limit=queries.get("limit", 10),
    )
    return DataListResponse(items=items, meta=meta)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_service.create_user(db, user_in)
    await db.commit()
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    db_user = await user_service.update_user(db, user_id, user_in)
    await db.commit()
    return db_user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user_service.delete_user(db, user_id)
    await db.commit()
    return db_user
