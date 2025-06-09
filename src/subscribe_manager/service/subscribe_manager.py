import asyncio
from subscribe_manager.common.log_util import get_logger
import nest_asyncio
from typing import Any, Tuple, List, Dict
from urllib.parse import urlparse, parse_qs
import aiohttp
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from subscribe_manager.database import DBManager
from subscribe_manager.service.base import load_subscribe_config
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import os
import uvicorn
from subscribe_manager.constant import (
    FILE_TYPE_MAP,
    TRANSFORM_ALLOWED,
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

logger = get_logger(__name__)

# FILE_TYPE_MAP = {"clash": "yaml", "surge": "conf", "surfboard": "conf"}
# TRANSFORM_ALLOWED = {"clash": ["surge", "surfboard"]}
# # DEFAULT_MAX_SUBSCRIBE_COUNT = 5
# DEFAULT_CONFIG_FILE = "config.yaml"
# DEFAULT_SUBSCRIBE_SAVE_PATH = "subscribe"
# DEFAULT_REFRESH_FLAG = True
# DEFAULT_INTERVAL_TYPE = "days"
# DEFAULT_INTERVAL = 1
# DEFAULT_START_DATE = "2000-01-01 00:00:00"
# DEFAULT_HOST = "127.0.0.1"
# DEFAULT_PORT = 8000
# DEFAULT_DB_NAME = "subscribe_manager.db"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
)

nest_asyncio.apply()  # 允许嵌套事件循环


def check_sensitive(sensitive_policy: List[Dict[str, str]], line: str) -> bool:
    for item in sensitive_policy:
        check_type = item["check_type"]
        keyword = item["keyword"]
        if check_type == "start":
            if line.startswith(keyword):
                return True
    return False


def get_target_value(url: str) -> str:
    # Parse the URL and extract query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    # Return the target value or the default if target is not present
    return query_params.get("target", ["unknown"])[0]


def save_to_file(file_path: str, file_name: str, data: str) -> None:
    if file_path:
        os.makedirs(file_path, exist_ok=True)
    with open(file_path + os.sep + file_name, "w", encoding="utf-8") as file:
        file.write(data)
    logger.info(f"Saved {file_name} to {file_path}")


async def _download_file(
    session: aiohttp.ClientSession,
    url: str,
    file_path: str,
    file_name: str,
    sensitive_policy: List[Dict[str, str]],
) -> tuple[bool, str, str]:
    file_full_name = os.path.join(file_path, file_name)
    try:
        # 发送请求下载文件
        headers = {"User-Agent": USER_AGENT}
        async with session.get(url, headers=headers, ssl=False) as response:
            response.raise_for_status()  # 检查请求是否成功
            response_content = await response.read()
            if len(response_content) == 0:
                logger.error(f"文件 {file_full_name} 下载失败，文件内容为空")
                return False, "", ""
            else:
                logger.info(f"文件 {file_full_name} 下载成功")
                subscription_userinfo = response.headers["subscription-userinfo"]
                content = "\n".join(
                    line
                    for line in response_content.decode("utf-8").splitlines()
                    if not check_sensitive(sensitive_policy, line)
                )
                return True, content, subscription_userinfo
    except Exception as e:
        logger.error(f"下载 {file_full_name} 失败: {e}")
        return False, "", ""


class SubscribeManager:
    def __init__(
        self,
        *,
        max_subscribe_count: int = DEFAULT_MAX_SUBSCRIBE_COUNT,
        config_file: str = DEFAULT_CONFIG_FILE,
        subscribe_save_path: str = DEFAULT_SUBSCRIBE_SAVE_PATH,
        refresh_flag: bool = DEFAULT_REFRESH_FLAG,
        interval_type: str = DEFAULT_INTERVAL_TYPE,
        interval: int = DEFAULT_INTERVAL,
        start_date: str = DEFAULT_START_DATE,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        db_name: str = DEFAULT_DB_NAME,
    ):
        """

        :param max_subscribe_count: 最大订阅次数
        :param config_file: 配置文件
        :param subscribe_save_path: 订阅内容本地保存路径
        :param refresh_flag: 是否刷新
        :param interval_type: 间隔类型 days, hours, minutes
        :param interval: 间隔时长
        :param start_date: 定时开始时间
        :param host: host
        :param port: port
        :param db_name: 数据库名称
        """
        logger.info(f"最大订阅次数: {max_subscribe_count}")
        logger.info(f"配置文件路径: {config_file}")
        logger.info(f"订阅保存路径: {subscribe_save_path}")
        logger.info(f"刷新标志: {refresh_flag}")
        logger.info(f"间隔类型: {interval_type}")
        logger.info(f"间隔时间: {interval}")
        logger.info(f"起始日期: {start_date}")

        self.max_subscribe_count = max_subscribe_count
        self.config_file = config_file
        self.config = self._load_config()
        self.subscribe_save_path = subscribe_save_path
        self.current_subscribe_count = 0
        self.db_manager = DBManager(db_name=db_name)
        self.refresh_flag = refresh_flag
        self.host = host
        self.port = port
        if self.refresh_flag:
            asyncio.run(self._download_from_config())
        self.scheduler = BackgroundScheduler()
        # 将定时任务添加到调度器中
        self.scheduler.add_job(
            self.download_job,
            trigger=IntervalTrigger(**{interval_type: interval, "start_date": start_date}),
            id="subscribe_update",
            replace_existing=True,
        )
        self.scheduler.start()

    def _load_config(self) -> Any:
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            return config  # 返回配置字典
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_file}")
            return None  # 如果文件未找到，返回 None
        except yaml.YAMLError as e:
            logger.error(f"解析 YAML 文件时出错: {e}")
            return None  # 如果 YAML 解析出错，返回 None

    async def _download_and_save(
        self,
        uuid: str,
        url: str,
        target: str,
        file_path: str,
        file_name: str,
        sensitive_policy: List[Any],
        auto_transform: bool,
    ) -> None:
        async with aiohttp.ClientSession() as session:
            success, subscribe_content, subscription_userinfo = await _download_file(
                session, url, file_path, file_name, sensitive_policy
            )

        if success:
            # 保存到文件
            save_to_file(file_path, file_name, subscribe_content)
            # 写入数据库
            self.db_manager.insert_or_update_subscribe(file_path + os.sep + file_name, url, subscription_userinfo)

            if auto_transform:
                # 加载
                subscribe_config = load_subscribe_config(file_path + os.sep + file_name, target)

                # 订阅转换
                for transform_target in TRANSFORM_ALLOWED.get(target, []):
                    transform_file_type = FILE_TYPE_MAP.get(transform_target, "unknown")
                    transform_content = subscribe_config.subscribe_transform(transform_target)
                    transform_file_name = uuid + "_" + transform_target + "." + transform_file_type
                    save_to_file(file_path, transform_file_name, transform_content)
                    # 写入数据库
                    self.db_manager.insert_or_update_subscribe(
                        file_path + os.sep + transform_file_name, url, subscription_userinfo
                    )

    async def _download_from_config(self) -> None:
        if self.config is None:
            return None
        services = self.config["services"]
        tasks = []
        for service in services.keys():
            sensitive_policy = services[service].get("sensitive_policy", [])
            auto_transform = services[service].get("auto_transform", "false") == "true"
            target_type = services[service].get("target_type")
            for url_info in services[service]["urls"]:
                uuid = url_info["uuid"]
                url = url_info["url"]
                # 未指定时，尝试根据 url 自动解析
                target = target_type or get_target_value(url)
                if target == "unknown":
                    raise ValueError(f"{url}未能获取订阅类型，请检查配置")
                file_type = FILE_TYPE_MAP.get(target, "unknown")
                if file_type == "unknown":
                    raise ValueError(f"{target}未能获取文件类型，请检查配置")
                file_path = self.subscribe_save_path + os.sep + service
                file_name = uuid + "_" + target + "." + file_type
                if self.current_subscribe_count < self.max_subscribe_count:
                    tasks.append(
                        self._download_and_save(
                            uuid, url, target, file_path, file_name, sensitive_policy, auto_transform
                        )
                    )
                self.current_subscribe_count += 1
        await asyncio.gather(*tasks)

    def download_job(self) -> None:
        # 重置订阅次数
        self.current_subscribe_count = 0
        # 重新加载订阅设置
        self.config = self._load_config()
        # 重新下载
        asyncio.run(self._download_from_config())

    def get_subscribe_info(self, service: str, uuid: str, target: str) -> Tuple[str, str, str]:
        file_type = FILE_TYPE_MAP.get(target, "unknown")
        file_name = self.subscribe_save_path + os.sep + service + os.sep + uuid + "_" + target + "." + file_type
        subscription_userinfo = ""
        logger.info(file_name)
        row = self.db_manager.query_subscribe(file_name)
        if row:
            subscription_userinfo = row[2]

        return file_name, subscription_userinfo, file_type

    def start(self) -> None:
        app = FastAPI()

        @app.get("/link/{service}/{file_id}")
        async def download(service: str, file_id: str, target: str = "clash") -> Any:
            # 文件路径，可以是相对路径或者绝对路径
            file_name, subscription_userinfo, file_type = self.get_subscribe_info(service, file_id, target)
            # 检查文件是否存在
            if os.path.exists(file_name):
                # 返回文件响应，media_type 表示内容类型
                return FileResponse(
                    file_name,
                    headers={"subscription-userinfo": subscription_userinfo},
                    media_type="text/plain",
                    filename=f"{service}.{file_type}",
                )
            else:
                return JSONResponse(content={"error": "File not found"}, status_code=404)

        uvicorn.run(app, host=self.host, port=self.port)
