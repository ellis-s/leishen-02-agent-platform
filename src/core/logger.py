# 本文件负责统一初始化项目日志。应用启动时调用 setup_logger()，
# 它会读取日志级别和目录配置，清除已有的输出目标，再配置控制台和文件输出。
#
# logger.add() 用于注册一个日志输出目标，并为该目标设置最低日志级别和输出格式。
# 它本身不记录日志；调用 logger.info()、logger.error() 等方法时，
# 符合级别要求的日志会分别发送到已注册的目标。本文件注册了两个目标：
# 1. 控制台（sys.stdout）：带颜色，方便实时查看。
# 2. 日志文件：方便回查，按日轮转，旧文件用 gzip 压缩，保留期限为 30 天。
import sys  # 提供标准输出 sys.stdout。
from pathlib import Path  # 用于拼接路径和创建日志目录。

from loguru import logger  # 项目各模块共享的 Loguru 日志对象。

from src.core.config import get_settings  # 读取日志级别和日志目录等应用配置。


# 通常在应用启动时调用；仅导入本模块不会配置日志。
def setup_logger() -> None:
    settings = get_settings()
    # 移除所有已注册的输出目标（包括默认的标准错误输出），避免重复配置。
    logger.remove()

    # 注册控制台输出，便于实时查看日志。
    logger.add(
        sys.stdout,  # 写到标准输出，而不是标准错误。
        level=settings.LOG_LEVEL,  # 只输出达到最低级别的日志，例如 INFO 及以上。
        # Python 会把括号内相邻的字符串拼成一条日志格式。
        format=(
            # 绿色时间戳，精确到毫秒。
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            # 日志级别左对齐到至少 8 个字符，并按级别着色。
            "<level>{level: <8}</level> | "
            # 用青色标出记录日志的模块名、函数名和行号。
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            # 日志正文也按级别着色。
            "<level>{message}</level>"
        ),
        colorize=True,  # 启用控制台颜色。
    )

    # 将配置中的目录转为 Path；父目录缺失时一起创建，目录已存在时不报错。
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 注册文件输出，便于事后排查。
    logger.add(
        # Loguru 在创建文件时展开日期。当前模板会保留文件名前导空格；
        # 若预期文件名为 YYYY-MM-DD.log，模板应写成 "{time:YYYY-MM-DD}.log"。
        str(log_dir / "{time: YYYY-MM-DD}.log"),
        level=settings.LOG_LEVEL,  # 与控制台使用相同的最低日志级别。
        # 文件日志不着色，时间精确到秒，其余字段与控制台一致。
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",  # 跨过午夜后，下一条写入的日志会触发轮转。
        retention="30 days",  # 轮转时清理超过 30 天的旧日志。
        compression="gz",  # 轮转后的旧文件用 gzip 压缩。
        encoding="utf-8",  # 以 UTF-8 编码写入日志文件。
    )
