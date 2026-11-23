from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool | None = True


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    model_config = {
        "from_attributes": True,  # 作用是 允许用对象的属性来校验/构造模型，而不只接受 dict 。
    }
