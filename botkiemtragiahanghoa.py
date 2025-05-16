from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
TOKEN = os.environ.get("BOT_TOKEN")

driver = webdriver.Chrome(ChromeDriverManager().install())

# Bật logging chi tiết cho debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Danh mục sản phẩm và URL tương ứng
DANH_MUC = {
    "Sữa tắm": "https://www.bachhoaxanh.com/sua-tam",
    "Dầu gội": "https://www.bachhoaxanh.com/dau-goi-dau",
    "Kem đánh răng": "https://www.bachhoaxanh.com/kem-danh-rang",
    "Nước giặt": "https://www.bachhoaxanh.com/nuoc-giat",
    "Nước xả": "https://www.bachhoaxanh.com/nuoc-xa-vai",
    "Bột giặt": "https://www.bachhoaxanh.com/bot-giat",
    "Nước rửa chén": "https://www.bachhoaxanh.com/nuoc-rua-chen",
    "Nước lau nhà": "https://www.bachhoaxanh.com/nuoc-lau-nha",
}

def create_driver():
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    chromedriver_path = "C:/Users/Admin/Desktop/JOB/Python/chromedriver.exe"

    chrome_options = Options()
    chrome_options.binary_location = brave_path
    chrome_options.add_argument("--headless")  # Mở nếu muốn chạy ẩn
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Giảm log

    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Bỏ dòng này nếu muốn thấy trình duyệt chạy
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def crawl_products(url):
    driver = None
    products = []
    seen_names = set()
    try:
        driver = create_driver()
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        container = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "#main-layout > div > div.flex.flex-wrap.content-stretch.bg-white.px-0"
        )))

        time.sleep(2)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

        product_cards = container.find_elements(By.CSS_SELECTOR, "div > div")

        for card in product_cards:
            if len(products) >= 20:
                break
            try:
                name_el = card.find_element(By.CSS_SELECTOR, "a > h3")
                name = name_el.text.strip()
                if name in seen_names:
                    continue

                # Giá hiện tại
                name_el = card.find_element(By.CSS_SELECTOR, "a > h3")
                name = name_el.text.strip()
                if not name or name in seen_names:
                    continue

                price_el = card.find_element(By.CSS_SELECTOR, "div.product_price")
                price = price_el.text.strip()

                # Giá gốc
                try:
                    price_origin_el = card.find_element(By.CSS_SELECTOR,
                        "div.mb-2px.block.leading-3 > span.line-through")
                    price_origin = price_origin_el.text.strip()
                except:
                    price_origin = None

                # % giảm giá
                try:
                    discount_el = card.find_element(By.CSS_SELECTOR,
                        "div.mb-2px.block.leading-3 > span:not(.line-through)")
                    discount = discount_el.text.strip()
                except:
                    discount = None

                # Ưu đãi đặc biệt (quà tặng)
                try:
                    gift_el = driver.find_element(By.CSS_SELECTOR,
                        "div.sticky.top-[100px] > div > div")
                    gift = gift_el.text.strip()
                except:
                    gift = None

                products.append({
                    "name": name,
                    "price": price,
                    "price_origin": price_origin,
                    "discount": discount,
                    "gift": gift,
                })
                seen_names.add(name)

            except Exception:
                continue

    except Exception as e:
        print("❌ Lỗi khi crawl:", e)
    finally:
        if driver:
            driver.quit()
    return products


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Chào bạn! Tôi là bot kiểm tra giá hàng hóa.\n"
        "Gõ /menu để xem danh mục sản phẩm có sẵn."
    )

def menu(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in DANH_MUC]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Chọn danh mục sản phẩm:", reply_markup=markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    ten_danh_muc = query.data
    url = DANH_MUC.get(ten_danh_muc)

    if not url:
        query.edit_message_text("Không tìm thấy danh mục.")
        return

    query.edit_message_text(f"🔄 Đang thu thập dữ liệu *{ten_danh_muc}*...", parse_mode='Markdown')

    products = crawl_products(url)

    if not products:
        query.edit_message_text("❌ Không thể thu thập dữ liệu sản phẩm bằng Selenium.")
        return

    text = f"📦 *{ten_danh_muc}* (Top {len(products)} sản phẩm):\n\n"

    for p in products:
        text += f"🛒 *{p['name']}*\n"
        text += f"💰 Giá: {p['price']}\n"
        if p['price_origin']:
            text += f"🔖 Giá gốc: {p['price_origin']}\n"
        if p['discount']:
            text += f"📉 Giảm giá: {p['discount']}\n"
        if p['gift']:
            text += f"🎁 Ưu đãi: {p['gift']}\n"
        text += "\n"

    query.edit_message_text(text.strip(), parse_mode='Markdown')

def main():
    TOKEN = "7833019833:AAELIJXE-tCrJ_kYiIUKRBh2VnbTHINey_E"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CallbackQueryHandler(button))

    logger.info("Bot đang chạy...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
