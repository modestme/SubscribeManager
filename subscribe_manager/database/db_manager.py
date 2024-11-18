from subscribe_manager.common.log_util import get_logger
import sqlite3
from typing import Any
from datetime import datetime
import os
from subscribe_manager.constant import BASE_DIR


logger = get_logger(__name__)


class DBManager:
    def __init__(self, db_name: str, db_recreate: bool = False):
        self.db_recreate = db_recreate
        self.db_name = db_name
        self.sql_dir = os.path.join(BASE_DIR, "static", "database", "sql")
        if self.db_recreate:
            if os.path.exists(db_name):
                os.remove(db_name)
        self._init_db()

    def _init_db(self) -> None:
        logger.info(f"Creating database {self.db_name}")
        file_dir = os.path.dirname(self.db_name)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            with open(os.path.join(self.sql_dir, "ddl", "subscribe_manager.sql"), "r") as f:
                cursor.execute(f.read())
            conn.commit()

    def insert_subscribe(self, file_name: str, url: str, subscription_userinfo: str) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(os.path.join(self.sql_dir, "dml", "insert.sql"), "r") as f:
                cursor.execute(f.read(), (file_name, url, subscription_userinfo, current_date, current_date))
            cursor.close()
            conn.commit()

    def update_subscribe(self, file_name: str, url: str, subscription_userinfo: str) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(os.path.join(self.sql_dir, "dml", "update.sql"), "r") as f:
                cursor.execute(f.read(), (url, subscription_userinfo, current_date, file_name))
            conn.commit()

    def query_subscribe(self, file_name: str) -> Any:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            with open(os.path.join(self.sql_dir, "dml", "query.sql"), "r") as f:
                cursor.execute(f.read(), (file_name,))
                return cursor.fetchone()

    def insert_or_update_subscribe(self, file_name: str, url: str, subscription_userinfo: str) -> None:
        row = self.query_subscribe(file_name)
        if row is None:
            self.insert_subscribe(file_name, url, subscription_userinfo)
            logger.info(f"Insert subscribe success: {file_name}, {url}, {subscription_userinfo}")
        else:
            self.update_subscribe(file_name, url, subscription_userinfo)
            logger.info(f"Update subscribe success: {file_name}, {url}, {subscription_userinfo}")

    def delete_subscribe(self, file_name: str) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            with open(os.path.join(self.sql_dir, "dml", "delete.sql"), "r") as f:
                cursor.execute(f.read(), (file_name,))
            conn.commit()
