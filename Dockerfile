# Image gốc có Python 3.8
FROM python:3.8-slim

# Cài các package cần thiết
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    chromium-driver \
    chromium \
    && apt-get clean

# Biến môi trường cho Selenium dùng Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/lib/chromium/"

# Tạo thư mục và copy code vào container
WORKDIR /app
COPY . /app

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Chạy bot
CMD ["python", "botkiemtragiahanghoa.py"]
