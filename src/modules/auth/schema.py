from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_code: str
    captcha_key: str


class LoginResponse(BaseModel):
    access_token: str
