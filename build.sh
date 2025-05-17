#!/bin/bash

# Cập nhật & cài đặt các gói cần thiết
apt-get update && apt-get install -y wget unzip curl gnupg

# Thêm repo Google & cài đặt Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update && apt-get install -y google-chrome-stable

# Tải chromedriver tương thích với Chrome
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | grep -A 10 "\"version\": \"$CHROME_VERSION" | grep -oP 'https.*chromedriver-linux64.zip' | head -1)
wget -O chromedriver.zip "$CHROMEDRIVER_VERSION"
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
