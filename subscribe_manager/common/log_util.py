import logging
import os
from typing import Any, Optional

import colorama

# 初始化 Colorama，用于终端颜色支持
colorama.init(autoreset=True)

COLORS = {
    "DEBUG": colorama.Fore.CYAN,
    "INFO": colorama.Fore.GREEN,
    "WARNING": colorama.Fore.YELLOW,
    "ERROR": colorama.Fore.RED,
    "CRITICAL": colorama.Back.RED + colorama.Fore.WHITE,
}


# 自定义 Formatter，支持颜色和代码行号
class Formatter(logging.Formatter):
    def __init__(self, *args: Any, use_color: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        # 可能会有多个 handle，不对原对象进行修改
        formatter_record = logging.makeLogRecord(record.__dict__)
        # 自定义日志时间
        if self.use_color:
            formatter_record.time = (
                f"{colorama.Fore.GREEN}{self.formatTime(formatter_record, self.datefmt)}{colorama.Style.RESET_ALL}"
            )
        else:
            formatter_record.time = self.formatTime(formatter_record, self.datefmt)
        # name
        if self.use_color:
            formatter_record.name = f"{colorama.Fore.CYAN}{formatter_record.name}{colorama.Style.RESET_ALL}"
        # funcName
        if self.use_color:
            formatter_record.funcName = f"{colorama.Fore.CYAN}{formatter_record.funcName}{colorama.Style.RESET_ALL}"
        # lineno
        if self.use_color:
            formatter_record.line_no = f"{colorama.Fore.CYAN}{formatter_record.lineno}{colorama.Style.RESET_ALL}"
        else:
            formatter_record.line_no = formatter_record.lineno
        # 为日志级别添加颜色
        if self.use_color:
            levelname_color = COLORS.get(formatter_record.levelname, colorama.Fore.GREEN)
            formatter_record.levelname = f"{levelname_color}{formatter_record.levelname}{colorama.Style.RESET_ALL}"
            # 日志信息与日志级别保持一致
            formatter_record.transform_message = (
                f"{levelname_color}{formatter_record.getMessage()}{colorama.Style.RESET_ALL}"
            )
        else:
            formatter_record.transform_message = formatter_record.getMessage()

        # 定义日志格式
        log_format = "%(time)s | %(levelname)s | %(name)s:%(funcName)s:%(line_no)s - %(transform_message)s"
        formatter = logging.Formatter(log_format)
        return formatter.format(formatter_record)


# 创建一个模块级的 Logger
def get_logger(
    name: str, *, log_level: Optional[int] = None, console_enable: Optional[bool] = None, log_file: Optional[str] = None
) -> logging.Logger:
    logger = logging.getLogger(name)

    log_level = log_level or int(os.getenv("SM_LOG_LEVEL", logging.DEBUG))
    console_enable = console_enable or os.getenv("SM_LOG_CONSOLE_ENABLE", "true") == "true"
    log_file = log_file or os.getenv("SM_LOG_FILE")

    logger.setLevel(log_level)  # 设置日志级别
    if not logger.handlers:
        if console_enable:
            # 创建 Handler 输出到终端
            handler = logging.StreamHandler()

            # 设置自定义 Formatter
            formatter = Formatter(use_color=True)
            handler.setFormatter(formatter)

            # 将 Handler 添加到 Logger
            logger.addHandler(handler)
        if log_file is not None:
            # 创建 Handler 输出到终端
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            # 设置自定义 Formatter
            formatter = Formatter(use_color=False)
            file_handler.setFormatter(formatter)

            # 将 Handler 添加到 Logger
            logger.addHandler(file_handler)

    return logger
