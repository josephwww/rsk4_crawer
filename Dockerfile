# 使用官方Python基础镜像
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the Chinese mirror for apt
# Create and set the Chinese mirror for apt
RUN echo 'deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free' >> /etc/apt/sources.list

# 安装必要的依赖
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    curl \
    chromium-driver \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

# 运行自动化脚本
CMD ["python", "main.py"]
