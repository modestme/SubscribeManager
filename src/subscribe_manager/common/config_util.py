import yaml
from subscribe_manager.config import settings
from subscribe_manager.common.log_util import get_logger

logger = get_logger(__name__)


def load_config_file(config_file: str) -> bool:
    # 读取配置文件
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_file}")
        return False
    except yaml.YAMLError as e:
        logger.error(f"解析 YAML 文件时出错: {e}")
        return False

    file_settings = config.get("settings", {})
    settings.max_subscribe_count = file_settings.get("max_subscribe_count", settings.max_subscribe_count)
    settings.subscribe_save_path = file_settings.get("subscribe_save_path", settings.subscribe_save_path)
    settings.refresh_flag = (
        file_settings.get("refresh_flag") == "true" if file_settings.get("refresh_flag") else settings.refresh_flag
    )
    settings.interval_type = file_settings.get("interval_type", settings.interval_type)
    settings.interval = file_settings.get("interval", settings.interval)
    settings.start_date = file_settings.get("start_date", settings.start_date)
    settings.host = file_settings.get("host", settings.host)
    settings.port = file_settings.get("port", settings.port)
    settings.db_name = file_settings.get("db_name", settings.db_name)

    return True
