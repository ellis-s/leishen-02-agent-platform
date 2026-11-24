import base64
import random
import string
from uuid import uuid4

from captcha.image import ImageCaptcha
from redis import Redis

from src.modules.captcha.schema import (
    CaptchaRead,
    CaptchaVerifyRequest,
)


class CaptchaService:
    EXPIRE_TIME = 5 * 60  # 5 分钟
    KEY_PREFIX = "captcha:"  # 验证码 key 前缀

    def __init__(self, redis: Redis):
        self.redis = redis

    def create_number(self) -> str:
        # 从大写字母和数字中随机生成长度为4的字符串， 并且把不易识别的字母替换为数字
        number = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(4)
        )
        return number.replace("O", "0").replace("I", "1").replace("L", "1")

    def generate_image(self, code: str) -> str:
        """
        生成验证码图片
        """
        captcha = ImageCaptcha()
        image = captcha.generate(code)
        image_base64 = base64.b64encode(image.read()).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"

    async def generate_captcha(self) -> CaptchaRead:
        """
        生成验证码

        1. 生成 4 位随机验证码
        2. 生成随机串作为验证码 key，过期时间为 5 分钟
        3. 生成 base64 编码的验证码图片
        4. 存入 redis 缓存，过期时间为 5 分钟
        5. 返回验证码图片和验证码 key
        """
        code = self.create_number()

        key = str(uuid4())

        # 生成验证码图片
        imgStr = self.generate_image(code)

        # 存入缓存
        await self.redis.set(
            f"{self.KEY_PREFIX}{key}", code.lower(), ex=self.EXPIRE_TIME
        )

        return CaptchaRead(key=key, image=imgStr)

    async def verify_captcha(self, request: CaptchaVerifyRequest) -> bool:
        """
        验证验证码
        """
        code = await self.redis.get(f"{self.KEY_PREFIX}{request.key}")

        is_correct = code == request.code.lower()

        if is_correct:
            await self.redis.delete(f"{self.KEY_PREFIX}{request.key}")

        return is_correct
