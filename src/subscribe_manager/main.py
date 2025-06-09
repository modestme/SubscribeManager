import argparse
from subscribe_manager.service import SubscribeManager
from subscribe_manager.constant import DEFAULT_CONFIG_FILE
from subscribe_manager.common import get_logger, load_config_file
from subscribe_manager.config import settings

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

    if not load_config_file(config_file):
        logger.info(f"配置文件 {config_file} 加载失败")

    sm = SubscribeManager(
        max_subscribe_count=settings.max_subscribe_count,
        config_file=config_file,
        subscribe_save_path=settings.subscribe_save_path,
        refresh_flag=settings.refresh_flag,
        interval_type=settings.interval_type,
        interval=settings.interval,
        start_date=settings.start_date,
        host=settings.host,
        port=settings.port,
        db_name=settings.db_name,
    )
    sm.start()


if __name__ == "__main__":
    main()
