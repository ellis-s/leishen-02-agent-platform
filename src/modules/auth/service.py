from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BizException
from src.modules.auth.schema import LoginRequest, LoginResponse
from src.modules.captcha.schema import CaptchaVerifyRequest
from src.modules.captcha.service import CaptchaService
from src.modules.user.service import UserService
from src.utils.jwt_utils import create_token
from src.utils.password_utils import verify_password


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis
        self.captcha_service = CaptchaService(redis)
        self.user_service = UserService(db)

    async def login(self, data: LoginRequest) -> LoginResponse:
        """
        1. 验证验证码是否正确
        2. 验证用户名是否存在
        3. 验证用户是否 active
        4. 验证密码是否正确
        5. 生成 JWT TOKEN 并返回
        """

        await self.captcha_service.verify_captcha(
            CaptchaVerifyRequest(key=data.captcha_key, code=data.captcha_code)
        )

        user = await self.user_service.repo.get_by_username(data.username)
        if not user:
            raise BizException(message="用户不存在")

        if not user.is_active:
            raise BizException(message="用户已被禁用")

        if not verify_password(data.password, user.hashed_password):
            raise BizException(message="密码错误")

        token = create_token(
            payload={
                "sub": user.id,
                "username": user.username,
                "email": user.email,
            }
        )
        return LoginResponse(access_token=token)
