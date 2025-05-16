from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
chromedriver_path = "C:/Users/Admin/Desktop/JOB/Python/chromedriver.exe"

chrome_options = Options()
chrome_options.binary_location = brave_path
# chrome_options.add_argument("--headless")  # Bật headless khi chạy thực tế
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.bachhoaxanh.com/sua-tam")

    # Chờ phần tử container sản phẩm xuất hiện (tối đa 15 giây)
    wait = WebDriverWait(driver, 15)
    container = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "#main-layout > div > div.flex.flex-wrap.content-stretch.bg-white.px-0.py-\\[8px\\]"
    )))

    # Cuộn trang xuống dưới để load hết sản phẩm (5 lần)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # đợi load

    # Lấy tất cả div con trong container (từng sản phẩm)
    product_divs = container.find_elements(By.CSS_SELECTOR, "div")

    print(f"Tìm thấy {len(product_divs)} sản phẩm")

    for p in product_divs:
        try:
            name = p.find_element(By.CSS_SELECTOR, ".product-title").text
            price = p.find_element(By.CSS_SELECTOR, ".product-price").text
            print(f"{name} - {price}")
        except:
            continue

finally:
    driver.quit()
