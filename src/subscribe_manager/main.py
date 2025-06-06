import argparse
import yaml
from subscribe_manager.service import SubscribeManager
from subscribe_manager.constant import (
    DEFAULT_MAX_SUBSCRIBE_COUNT,
    DEFAULT_CONFIG_FILE,
    DEFAULT_SUBSCRIBE_SAVE_PATH,
    DEFAULT_REFRESH_FLAG,
    DEFAULT_INTERVAL_TYPE,
    DEFAULT_INTERVAL,
    DEFAULT_START_DATE,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_DB_NAME,
)
from subscribe_manager.common.log_util import get_logger

logger = get_logger(__name__)


def main() -> None:
    # 创建 ArgumentParser 实例
    parser = argparse.ArgumentParser(description="Subscribe Manager CLI - A tool to manage subscribe")

    # 添加参数
    parser.add_argument("--config_file", type=str, required=False, default=DEFAULT_CONFIG_FILE)

    # 解析参数
    args = parser.parse_args()
    config_file = args.config_file
    logger.info(f"配置文件路径 {config_file}")

    # 读取配置文件
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_file}")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"解析 YAML 文件时出错: {e}")
        exit(1)
    settings = config.get("settings", {})
    max_subscribe_count = settings.get("max_subscribe_count", DEFAULT_MAX_SUBSCRIBE_COUNT)
    subscribe_save_path = settings.get("subscribe_save_path", DEFAULT_SUBSCRIBE_SAVE_PATH)
    refresh_flag = settings.get("refresh_flag", DEFAULT_REFRESH_FLAG)
    interval_type = settings.get("interval_type", DEFAULT_INTERVAL_TYPE)
    interval = settings.get("interval", DEFAULT_INTERVAL)
    start_date = settings.get("start_date", DEFAULT_START_DATE)
    host = settings.get("host", DEFAULT_HOST)
    port = settings.get("port", DEFAULT_PORT)
    db_name = settings.get("db_name", DEFAULT_DB_NAME)

    sm = SubscribeManager(
        max_subscribe_count=max_subscribe_count,
        config_file=config_file,
        subscribe_save_path=subscribe_save_path,
        refresh_flag=refresh_flag,
        interval_type=interval_type,
        interval=interval,
        start_date=start_date,
        host=host,
        port=port,
        db_name=db_name,
    )
    sm.start()


if __name__ == "__main__":
    main()
