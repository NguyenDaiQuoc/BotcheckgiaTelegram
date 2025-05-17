from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import asyncio
from playwright.sync_api import sync_playwright
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
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
    )
     # Đường dẫn mặc định Railway/Render tải chromedriver
    chrome_path = "/usr/bin/google-chrome"
    driver_path = "/usr/bin/chromedriver"
    chrome_options.binary_location = chrome_path    
    # Tự động tải chromedriver phù hợp
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

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
    products = []
    seen_names = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=60000)

            page.wait_for_selector("#main-layout div.flex.flex-wrap.content-stretch.bg-white.px-0", timeout=10000)

            for _ in range(5):
                page.mouse.wheel(0, 5000)
                time.sleep(1)

            product_cards = page.query_selector_all("div.flex.flex-wrap.content-stretch.bg-white.px-0 > div > div")

            for card in product_cards:
                if len(products) >= 20:
                    break
                try:
                    name_el = card.query_selector("a > h3")
                    if not name_el:
                        continue
                    name = name_el.inner_text().strip()
                    if name in seen_names:
                        continue

                    price_el = card.query_selector("div.product_price")
                    price = price_el.inner_text().strip() if price_el else "?"

                    price_origin_el = card.query_selector("div.mb-2px.block.leading-3 > span.line-through")
                    price_origin = price_origin_el.inner_text().strip() if price_origin_el else None

                    discount_el = card.query_selector("div.mb-2px.block.leading-3 > span:not(.line-through)")
                    discount = discount_el.inner_text().strip() if discount_el else None

                    gift_el = card.query_selector("div.sticky.top-[100px] > div > div")
                    gift = gift_el.inner_text().strip() if gift_el else None

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

            browser.close()
    except Exception as e:
        print("❌ Lỗi khi crawl với Playwright:", e)

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
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="❌ Không thể thu thập dữ liệu sản phẩm bằng Selenium.")
        return

    for p in products:
        caption = f"🛒 *{p['name']}*\n💰 Giá: {p['price']}\n"
        if p['price_origin']:
            caption += f"🔖 Giá gốc: {p['price_origin']}\n"
        if p['discount']:
            caption += f"📉 Giảm giá: {p['discount']}\n"
        if p['gift']:
            caption += f"🎁 Ưu đãi: {p['gift']}"

        if p['image']:
            context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=p['image'],
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=caption,
                parse_mode='Markdown'
            )


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
