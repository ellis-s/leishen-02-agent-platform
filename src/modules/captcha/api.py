import redis
from fastapi import APIRouter, Depends

from src.core.base_schema import ResponseSchema
from src.infra.redis_cache import get_redis
from src.modules.captcha.schema import (
    CaptchaRead,
    CaptchaVerifyRequest,
)
from src.modules.captcha.service import CaptchaService


def get_service(redis: redis.Redis = Depends(get_redis)):
    """
    获取验证码服务
    """
    return CaptchaService(redis)


captchaRouter = router = APIRouter(prefix="/captcha", tags=["验证码"])


# 生成验证码
@router.get("/generate", response_model=ResponseSchema[CaptchaRead])
async def get_captcha(service: CaptchaService = Depends(get_service)):
    """
    生成验证码
    """

    data = await service.generate_captcha()

    return ResponseSchema(data=data)


# 验证验证码
@router.post("/verify", response_model=ResponseSchema[bool])
async def verify_captcha(
    request: CaptchaVerifyRequest,
    service: CaptchaService = Depends(get_service),
):
    """
    验证验证码
    """
    data = await service.verify_captcha(request)
    return ResponseSchema(data=data)
