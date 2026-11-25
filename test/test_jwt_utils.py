from datetime import timedelta

import pytest

from src.core.exceptions import BizException
from src.utils.jwt_utils import create_token, decode_token, verify_token


def test_create_verify_and_decode_token():
    payload = {"sub": 1001, "username": "alice", "is_superuser": False}
    token = create_token(payload)

    # 原始 payload 不应被修改
    assert payload == {"sub": 1001, "username": "alice", "is_superuser": False}
    assert isinstance(token, str)
    assert verify_token(token) is True

    decoded = decode_token(token)
    assert decoded["sub"] == "1001"
    assert decoded["username"] == "alice"
    assert decoded["is_superuser"] is False
    assert "iat" in decoded
    assert "exp" in decoded


def test_expired_token():
    token = create_token({"sub": "user-1"}, expires_delta=timedelta(seconds=-1))

    assert verify_token(token) is False

    with pytest.raises(BizException) as exc_info:
        decode_token(token)
    assert exc_info.value.code == 401
    assert exc_info.value.message == "认证令牌已过期"

    # verify=False 时允许解析过期令牌中的载荷
    unverified = decode_token(token, verify=False)
    assert unverified["sub"] == "user-1"


def test_invalid_signature_and_malformed_token():
    token = create_token(
        {"sub": "user-2"}, secret_key="first-secret-key-with-32-bytes!!"
    )

    assert verify_token(token, secret_key="second-secret-key-with-32-bytes!") is False
    with pytest.raises(BizException) as exc_info:
        decode_token(token, secret_key="second-secret-key-with-32-bytes!")
    assert exc_info.value.code == 401
    assert exc_info.value.message == "无效的认证令牌"

    assert verify_token("not-a-jwt-token") is False
    assert verify_token("") is False
    with pytest.raises(BizException) as exc_info:
        decode_token("not-a-jwt-token")
    assert exc_info.value.code == 401


def test_empty_secret_key_raises_value_error():
    with pytest.raises(ValueError):
        create_token({"sub": "1"}, secret_key="")

    with pytest.raises(ValueError):
        verify_token("abc.def.ghi", secret_key="")

    with pytest.raises(ValueError):
        decode_token("abc.def.ghi", secret_key="")
