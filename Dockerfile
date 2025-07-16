ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY


FROM python:3.11-slim

ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

RUN poetry --version

COPY pyproject.toml .

RUN cat pyproject.toml



RUN poetry install --no-root

COPY . .

CMD ["python", "src/subscribe_manager/main.py"] 