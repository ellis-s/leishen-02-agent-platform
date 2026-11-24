from pydantic import BaseModel


class CaptchaVerifyRequest(BaseModel):
    """
    生成验证码请求参数
    """

    key: str
    code: str


class CaptchaRead(BaseModel):
    """
    验证码响应参数
    """

    key: str
    image: str
