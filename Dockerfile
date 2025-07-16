FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

COPY prproject.toml .

RUN poetry install --no-root

COPY . .

CMD ["python", "src/subscribe_manager/main.py"] 