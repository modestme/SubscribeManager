FROM python:3.11-slim

# ENV http_proxy=${http_proxy:-}
# ENV https_proxy=${https_proxy:-}
# ENV HTTP_PROXY=${HTTP_PROXY:-}
ENV QYC_TEST1=${HTTPS_PROXY}
ENV QYC_TEST2=$HTTPS_PROXY

RUN echo "http_proxy=$http_proxy" && \
    echo "https_proxy=$https_proxy" && \
    echo "HTTP_PROXY=$HTTP_PROXY" && \
    echo "HTTPS_PROXY=$HTTPS_PROXY" && \
    echo "QYC_TEST1=$QYC_TEST1" && \
    echo "QYC_TEST2=$QYC_TEST2"

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry     

RUN poetry --version

COPY pyproject.toml .

RUN cat pyproject.toml



RUN poetry install --no-root

COPY . .

CMD ["python", "src/subscribe_manager/main.py"] 