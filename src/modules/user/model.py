# ORM 模型 =》 数据库表

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import MyBaseModel


class User(MyBaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="用户名"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="邮箱"
    )
    hashed_password: Mapped[str] = mapped_column(String(100), comment="密码哈希")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否是超级管理员"
    )
    last_login_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )
