# Sử dụng Python base image
FROM python:3.12-slim

# Cài đặt Chrome + các tiện ích
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils libu2f-udev \
    libvulkan1 libdrm2 libgbm1 libxshmfence1 chromium && \
    rm -rf /var/lib/apt/lists/*

# Cài chromedriver tự động
RUN pip install webdriver-manager

# Copy file bot
WORKDIR /app
COPY . /app

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Mặc định chạy bot
CMD ["python", "botkiemtragiahanghoa.py"]
