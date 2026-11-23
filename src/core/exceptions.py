from fastapi import FastAPI, Request
from loguru import logger
from starlette.responses import JSONResponse


class BizException(Exception):
    """业务异常"""

    def __init__(self, code: int = 400, message: str = "业务异常") -> None:
        self.code = code
        self.message = message


def register_exception_handler(app: FastAPI):
    @app.exception_handler(BizException)
    async def biz_exception_handler(request: Request, exc: BizException):
        return JSONResponse(
            status_code=200,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部异常", "data": None},
        )
