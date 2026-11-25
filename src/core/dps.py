from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BizException
from src.infra.database import get_db
from src.modules.user.model import User
from src.modules.user.schema import UserRead
from src.utils.jwt_utils import decode_token, outh2_schema


async def get_current_user(
    token: str = Depends(outh2_schema),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    获取当前用户
    """
    try:
        payload = decode_token(token=token)
        logger.info("payload is  ===>", payload)
        user_id = int(payload.get("sub"))
    except HTTPException:
        raise BizException(code=401, message="token 无效")

    user = await db.get(User, user_id)

    if not user:
        raise BizException(code=401, message="用户不存在")
    if not user.is_active:
        raise BizException(code=401, message="用户被禁用")

    return UserRead.model_validate(user)
