from dotenv import load_dotenv
load_dotenv()

import os
import logging
from pathlib import Path
from flask import Flask, request
from telebot import TeleBot, types
from openai import OpenAI

# Agents
from h_agent import HAgent  # نسخه دیجیتال حسین

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

# Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    log.error("TELEGRAM_TOKEN or OPENAI_API_KEY missing!")
    raise ValueError("Required variables missing")

# Initialize
bot = TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

user_state = {}  # وضعیت کاربر: "catalog", "cut", "digital", etc.
IMG_PATH = Path("images")  # پوشه عکس‌ها

# Agents
h_agent = HAgent()  # نسخه دیجیتال حسین

# Keyboards
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📋 کاتالوگ محصولات", "✂️ برش بهینه")
    kb.add("🧠 مشاوره سریع", "📦 ثبت سفارش")
    kb.add("💻 نسخه دیجیتال حسین")
    return kb

# Command Handlers
@bot.message_handler(commands=["start"])
def start(msg):
    try:
        with open(IMG_PATH / "welcome.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "🌳 سلام دوست من!\n"
                    "به کارگاه دیجیتال حسین تراب‌پرور خوش اومدی 🛠️\n"
                    "۱۵ سال تجربه نجاری و MDF کاری در خدمتتم\n"
                    "هر چی بخوای می‌سازم، راهنمایی می‌کنم، برات محاسبه می‌کنم!\n\n"
                    "از منوی زیر انتخاب کن 👇"
                ),
                reply_markup=main_menu()
            )
    except Exception as e:
        log.error(f"[Start Error] {e}")
        bot.send_message(msg.chat.id, "سلام! آماده‌ام کمکت کنم 🛠️", reply_markup=main_menu())

# Button Handlers
@bot.message_handler(func=lambda m: m.text == "📋 کاتالوگ محصولات")
def catalog(msg):
    user_state[msg.chat.id] = "catalog"
    try:
        with open(IMG_PATH / "catalog.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption="📸 کاتالوگ کارهای اخیرم:\nکابینت، کمد، میز، دکور و...\nعکس‌ها رو ببین، اگر خوشت اومد بگو برات مشابهش رو طراحی کنم!"
            )
    except:
        bot.send_message(msg.chat.id, "کاتالوگ آماده‌ست! بگو چی می‌خوای تا برات نمونه بفرستم.")
    bot.send_message(msg.chat.id, "برگشت به منو:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "✂️ برش بهینه")
def cut_optimize(msg):
    user_state[msg.chat.id] = "cut"
    try:
        with open(IMG_PATH / "cut.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption="✂️ برش بهینه MDF — کمترین پرتی، بیشترین صرفه!\n\nابعاد ورق اصلی رو بفرست (مثال: 183x366)"
            )
    except:
        bot.send_message(msg.chat.id, "ابعاد ورق اصلی رو بفرست (مثال: 183x366)")
    # ادامه در chat handler

@bot.message_handler(func=lambda m: m.text == "🧠 مشاوره سریع")
def quick_consult(msg):
    user_state[msg.chat.id] = "quick_ai"
    try:
        with open(IMG_PATH / "consult.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption="سوالت چیه؟\nنجاری، ابزار، چوب، MDF، ایمنی، هزینه... هر چی بپرس جواب می‌دم!"
            )
    except:
        bot.send_message(msg.chat.id, "سوالت چیه؟ هر چی بپرس جواب می‌دم 🧠")

@bot.message_handler(func=lambda m: m.text == "📦 ثبت سفارش")
def order(msg):
    user_state[msg.chat.id] = "order"
    bot.send_message(
        msg.chat.id,
        "📦 عالی! سفارش رو ثبت کنیم\n"
        "نام، شماره تماس و توضیحات کامل (ابعاد، طرح، نوع چوب، رنگ...) رو بنویس.\n"
        "به زودی باهات تماس می‌گیرم."
    )

@bot.message_handler(func=lambda m: m.text == "💻 نسخه دیجیتال حسین")
def digital_hossein(msg):
    user_state[msg.chat.id] = "digital_hossein"
    try:
        with open(IMG_PATH / "hossein.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "سلام دوست من! 😊\n"
                    "من حسین تراب‌پرورم — نجار حرفه‌ای با ۱۵ سال سابقه\n"
                    "اینجا نسخه دیجیتال منم، ولی دقیقاً مثل خودم جواب می‌دم 🛠️\n"
                    "هر سوالی داری بپرس — از طراحی کابینت تا تعمیر مبل، همه رو بلدم!\n"
                    "بگو ببینم، چی می‌خوای بسازی؟ 🌲"
                )
            )
    except Exception as e:
        log.error(f"[Digital Hossein Photo Error] {e}")
        bot.send_message(
            msg.chat.id,
            "سلام! من حسین تراب‌پرورم 🛠️\n"
            "۱۵ سال تجربه نجاری و MDF دارم و آماده‌ام کمکت کنم.\n"
            "سوالت چیه؟"
        )

# General Chat Handler
@bot.message_handler(func=lambda m: True)
def chat(msg):
    state = user_state.get(msg.chat.id, None)

    if state == "digital_hossein":
        try:
            reply = h_agent.generate_response(msg.text)
            bot.send_message(msg.chat.id, reply)
        except Exception as e:
            log.error(f"[H Agent Error] {e}")
            bot.send_message(msg.chat.id, "متاسفانه الان نمی‌تونم جواب بدم 😔 دوباره امتحان کن.")

    elif state == "quick_ai":
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": msg.text}]
            )
            bot.send_message(msg.chat.id, response.choices[0].message.content)
        except Exception as e:
            bot.send_message(msg.chat.id, "خطا در هوش مصنوعی — دوباره امتحان کن.")

    elif state == "cut":
        # اینجا بعداً برش بهینه رو اضافه می‌کنیم
        bot.send_message(msg.chat.id, "در حال توسعه برش بهینه پیشرفته... به زودی!")

    elif state == "order":
        bot.send_message(msg.chat.id, "سفارشت ثبت شد! به زودی تماس می‌گیرم 🙏", reply_markup=main_menu())
        # می‌تونی اینجا فوروارد به ادمین اضافه کنی

    else:
        bot.send_message(msg.chat.id, "از منوی زیر انتخاب کن 👇", reply_markup=main_menu())

# Flask Webhook
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "نجاری حسین تراب‌پرور آنلاینه 🛠️"

if __name__ == "__main__":
    log.info("بات نجاری حسین تراب‌پرور در حال اجراست...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


