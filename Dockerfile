FROM python:3.12-slim

# Cài chromium và các dependency cần thiết
RUN apt-get update && apt-get install -y \
    chromium-driver chromium \
    python3-pip \
    fonts-liberation \
    libatk-bridge2.0-0 libatk1.0-0 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libu2f-udev libvulkan1 libgbm1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập biến môi trường cho chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin/chromium"

# Cài pip packages
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Run bot
CMD ["python", "botkiemtragiahanghoa.py"]
