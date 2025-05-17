#!/bin/bash

# Cài đặt Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt update && apt install -y ./google-chrome-stable_current_amd64.deb

# Cài đặt chromedriver tương thích
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1)
wget https://chromedriver.storage.googleapis.com/$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/bin/chromedriver
