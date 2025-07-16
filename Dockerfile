FROM python:3.11

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

COPY pyproject.toml .

RUN poetry install --no-root

COPY . .

RUN poetry install

WORKDIR /app/src

CMD ["python", "-m", "subscribe_manager.main"] 