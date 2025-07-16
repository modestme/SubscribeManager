FROM python:3.11-slim 

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

COPY pyproject.toml .

RUN poetry install --no-root

COPY . .

RUN poetry install

CMD ["python", "src/subscribe_manager/main.py"] 