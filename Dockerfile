FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

# 关闭 poetry 虚拟环境功能
RUN poetry config virtualenvs.create false    

COPY pyproject.toml .

RUN poetry install --no-root

COPY . .

RUN poetry install

ENV SM_LOG_FILE=/var/log/subscribe-manager/subscribe_manager.log

WORKDIR /

CMD ["sbscmgr", "--config", "/etc/subscribe-manager/config.yaml", "--subscribe_save_path", "/var/opt/subscribe-manager/downloads", "--db_name", "/var/opt/subscribe-manager/subscribe_manager.db", "--refresh_flag", "true", "--host", "0.0.0.0"]