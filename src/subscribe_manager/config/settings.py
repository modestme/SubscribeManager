import os

import yaml
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from subscribe_manager import constant

# 根据 .env 文件，加载环境变量
env = os.getenv("PROJECT_ENV", default="").lower()
env_file_path = os.path.join(os.getcwd(), ".env" + env if env == "" else ".env." + env)
load_dotenv(dotenv_path=env_file_path, verbose=True)


class Settings(BaseSettings):
    max_subscribe_count: int = constant.DEFAULT_MAX_SUBSCRIBE_COUNT
    subscribe_save_path: str = constant.DEFAULT_SUBSCRIBE_SAVE_PATH
    refresh_flag: bool = constant.DEFAULT_REFRESH_FLAG
    interval_type: str = constant.DEFAULT_INTERVAL_TYPE
    interval: int = constant.DEFAULT_INTERVAL
    start_date: str = constant.DEFAULT_START_DATE
    host: str = constant.DEFAULT_HOST
    port: int = constant.DEFAULT_PORT
    db_name: str = constant.DEFAULT_DB_NAME

    log_level: int = int(os.getenv("SM_LOG_LEVEL", constant.DEFAULT_LOG_LEVEL))
    log_console_enable: bool = os.getenv("SM_LOG_CONSOLE_ENABLE") == "true" or constant.DEFAULT_CONSOLE_ENABLE
    log_file: str = os.getenv("SM_LOG_FILE", constant.DEFAULT_LOG_FILE)


settings = Settings()


def update_settings_from_file(config_file: str) -> None:
    # 读取配置文件
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        raise Exception(f"配置文件未找到: {config_file}")
    except yaml.YAMLError as e:
        raise Exception(f"解析 YAML 文件时出错: {e}")

    file_settings = config.get("settings", {})
    settings.max_subscribe_count = file_settings.get("max_subscribe_count", settings.max_subscribe_count)
    settings.subscribe_save_path = file_settings.get("subscribe_save_path", settings.subscribe_save_path)
    settings.refresh_flag = file_settings.get("refresh_flag", settings.refresh_flag)
    settings.interval_type = file_settings.get("interval_type", settings.interval_type)
    settings.interval = file_settings.get("interval", settings.interval)
    settings.start_date = file_settings.get("start_date", settings.start_date)
    settings.host = file_settings.get("host", settings.host)
    settings.port = file_settings.get("port", settings.port)
    settings.db_name = file_settings.get("db_name", settings.db_name)
