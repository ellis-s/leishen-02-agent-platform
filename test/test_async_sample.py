import asyncio

import pytest


async def async_add(a, b):
    await asyncio.sleep(1)
    return a + b


@pytest.mark.asyncio
async def test_async_add():
    print("异步测试...")
    result = await async_add(1, 2)
    assert result == 3
