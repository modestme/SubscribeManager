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

WORKDIR /app/src

CMD ["python", "-m", "subscribe_manager.main"] 