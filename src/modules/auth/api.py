from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import ResponseSchema
from src.infra.database import get_db
from src.infra.redis_cache import get_redis
from src.modules.auth.schema import LoginRequest, LoginResponse
from src.modules.auth.service import AuthService

# 登录

auth_router = router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, redis)


@router.post("/login", response_model=ResponseSchema[LoginResponse])
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):

    response = await service.login(data)

    return ResponseSchema(data=response)
