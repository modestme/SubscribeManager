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
    parser.add_argument("--max_subscribe_count", type=int, required=False)
    parser.add_argument("--subscribe_save_path", type=str, required=False)
    parser.add_argument("--refresh_flag", type=bool, required=False)
    parser.add_argument("--interval_type", type=str, required=False)
    parser.add_argument("--interval", type=int, required=False)
    parser.add_argument("--start_date", type=str, required=False)
    parser.add_argument("--host", type=str, required=False)
    parser.add_argument("--port", type=int, required=False)
    parser.add_argument("--db_name", type=str, required=False)

    # 解析参数
    args = parser.parse_args()
    config_file = args.config_file

    # 更新配置
    settings.max_subscribe_count = (
        args.max_subscribe_count if args.max_subscribe_count else settings.max_subscribe_count
    )
    settings.subscribe_save_path = (
        args.subscribe_save_path if args.subscribe_save_path else settings.subscribe_save_path
    )
    settings.refresh_flag = args.refresh_flag if args.refresh_flag else settings.refresh_flag
    settings.interval_type = args.interval_type if args.interval_type else settings.interval_type
    settings.interval = args.interval if args.interval else settings.interval
    settings.start_date = args.start_date if args.start_date else settings.start_date
    settings.host = args.host if args.host else settings.host
    settings.port = args.port if args.port else settings.port
    settings.db_name = args.db_name if args.db_name else settings.db_name

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
