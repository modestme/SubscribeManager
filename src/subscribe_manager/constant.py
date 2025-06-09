from os import path

# 模块路径
BASE_DIR = path.dirname(__file__)
# 订阅类型与文件类型的订阅关系
FILE_TYPE_MAP = {"clash": "yaml", "surge": "conf", "surfboard": "conf"}
# 支持的订阅转换
TRANSFORM_ALLOWED = {"clash": ["surge", "surfboard"]}
# 默认最大订阅次数
DEFAULT_MAX_SUBSCRIBE_COUNT = 5
# 默认配置文件路径
DEFAULT_CONFIG_FILE = "config.yaml"
# 默认订阅保存路径
DEFAULT_SUBSCRIBE_SAVE_PATH = "subscribe"
# 默认刷新标志
DEFAULT_REFRESH_FLAG = True
# 默认间隔类型
DEFAULT_INTERVAL_TYPE = "days"
# 默认间隔时长
DEFAULT_INTERVAL = 1
# 默认定时开始时间
DEFAULT_START_DATE = "2000-01-01 00:00:00"
# 默认HOST
DEFAULT_HOST = "127.0.0.1"
# 默认PORT
DEFAULT_PORT = 8000
# 默认数据库名称
DEFAULT_DB_NAME = "subscribe_manager.db"
# 日志默认配置
DEFAULT_LOG_LEVEL = 10
DEFAULT_CONSOLE_ENABLE = True
DEFAULT_LOG_FILE = "logs/subscribe_manager.log"
