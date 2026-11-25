from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.core.config import get_settings
from src.core.exceptions import register_exception_handler
from src.core.logger import setup_logger
from src.infra.database import my_async_engine
from src.middelware.logging import LoggingMiddleware
from src.modules.auth.api import auth_router
from src.modules.captcha.api import captchaRouter
from src.modules.user.api import router_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    settings = get_settings()
    logger.info(f"{settings.APP_NAME} 应用启动!! | env={settings.APP_ENV}")
    yield
    await my_async_engine.dispose()
    logger.info(f"{settings.APP_NAME} 应用关闭!!")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        version="1.0.0",
        lifespan=lifespan,
    )

    # 注册异常处理
    register_exception_handler(app)

    # 注册路由
    app.include_router(router_user, prefix="/api/v1")
    app.include_router(captchaRouter, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")

    # 注册中间件
    app.add_middleware(LoggingMiddleware)

    return app


app = create_app()


@app.get("/health")
async def health():
    return {"status": "ok"}
