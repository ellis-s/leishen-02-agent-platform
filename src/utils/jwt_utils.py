from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer

from src.core.config import get_settings
from src.core.exceptions import BizException

outh2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _resolve_secret_key(secret_key: str | None) -> str:
    key = get_settings().JWT_SECRET_KEY if secret_key is None else secret_key
    if not key:
        raise ValueError("JWT secret_key 不能为空")
    return key


def _resolve_algorithm(algorithm: str | None) -> str:
    alg = get_settings().JWT_ALGORITHM if algorithm is None else algorithm
    if not alg:
        raise ValueError("JWT algorithm 不能为空")
    return alg


def _resolve_algorithms(algorithms: list[str] | None) -> list[str]:
    algs = [get_settings().JWT_ALGORITHM] if algorithms is None else list(algorithms)
    if not algs:
        raise ValueError("JWT algorithms 不能为空")
    return algs


def create_token(
    payload: dict[str, Any],
    expires_delta: timedelta | None = None,
    secret_key: str | None = None,
    algorithm: str | None = None,
) -> str:
    """
    1. 生成 JWT

    :param payload: 需要编码到令牌中的载荷数据
    :param expires_delta: 自定义过期时长；未传时使用配置中的 JWT_EXPIRE_MINUTES
    :param secret_key: 签名密钥；未传时使用配置中的 JWT_SECRET_KEY
    :param algorithm: 签名算法；未传时使用配置中的 JWT_ALGORITHM
    :return: 签名后的 JWT 字符串
    """
    settings = get_settings()
    key = _resolve_secret_key(secret_key)
    alg = _resolve_algorithm(algorithm)

    to_encode = payload.copy()
    # PyJWT 2.10+ 要求标准字段 sub 为字符串，避免传入整型 user_id 时解码报错
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])

    now = datetime.now(UTC)
    to_encode.setdefault("iat", now)
    if expires_delta is not None:
        to_encode["exp"] = now + expires_delta
    elif "exp" not in to_encode:
        to_encode["exp"] = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    return jwt.encode(to_encode, key, algorithm=alg)


def verify_token(
    token: str,
    secret_key: str | None = None,
    algorithms: list[str] | None = None,
) -> bool:
    """
    2. 验证 JWT 是否有效（校验签名与过期时间等标准字段）

    :param token: 待验证的 JWT 字符串
    :param secret_key: 验证密钥；未传时使用配置中的 JWT_SECRET_KEY
    :param algorithms: 允许的算法列表；未传时使用配置中的 JWT_ALGORITHM
    :return: 有效返回 True，否则返回 False
    """
    key = _resolve_secret_key(secret_key)
    algs = _resolve_algorithms(algorithms)

    if not token or not isinstance(token, str):
        return False

    try:
        jwt.decode(token, key, algorithms=algs)
    except jwt.PyJWTError:
        return False
    return True


def decode_token(
    token: str,
    verify: bool = True,
    secret_key: str | None = None,
    algorithms: list[str] | None = None,
) -> dict[str, Any]:
    """
    3. 解析 JWT 获取载荷数据

    :param token: 待解析的 JWT 字符串
    :param verify: 是否校验签名与过期时间，默认 True；为 False 时仅解码载荷
    :param secret_key: 验证密钥；未传时使用配置中的 JWT_SECRET_KEY
    :param algorithms: 允许的算法列表；未传时使用配置中的 JWT_ALGORITHM
    :return: 解析后的载荷字典
    :raises BizException: 令牌过期或无效时抛出 401 业务异常
    """
    if verify:
        key = _resolve_secret_key(secret_key)
        algs = _resolve_algorithms(algorithms)

    if not token or not isinstance(token, str):
        raise BizException(code=401, message="无效的认证令牌")

    try:
        if verify:
            return jwt.decode(token, key, algorithms=algs)
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.ExpiredSignatureError as exc:
        raise BizException(code=401, message="认证令牌已过期") from exc
    except jwt.PyJWTError as exc:
        raise BizException(code=401, message="无效的认证令牌") from exc
