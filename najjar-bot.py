from dotenv import load_dotenv
load_dotenv()

import os
import logging
from pathlib import Path
from flask import Flask, request
from telebot import TeleBot, types
from openai import OpenAI

# Agent
from core.h_agent import h_agent

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

user_state = {}
IMG_PATH = Path("images")

# Keyboards
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📋 کاتالوگ محصولات", "✂️ برش بهینه")
    kb.add("📞 تماس با من", "📦 ثبت سفارش")
    kb.add("💻 نسخه دیجیتال حسین")
    return kb

# Start
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
        log.error(f"[Start Photo Error] {e}")
        bot.send_message(
            msg.chat.id,
            "سلام! حسین تراب‌پرور هستم 🛠️\nآماده‌ام کمکت کنم.\nاز منو انتخاب کن:",
            reply_markup=main_menu()
        )

# Button Handlers
@bot.message_handler(func=lambda m: m.text == "📋 کاتالوگ محصولات")
def catalog(msg):
    user_state[msg.chat.id] = "catalog"
    try:
        with open(IMG_PATH / "catalog.jpg", "rb") as photo:
            bot.send_photo(
                msg.chat.id,
                photo,
                caption="📸 کاتالوگ کارهای اخیرم:\nکابینت، کمد، میز، دکور و...\nاگر خوشت اومد، بگو برات مشابهش رو طراحی کنم!"
            )
    except Exception as e:
        log.error(f"[Catalog Photo Error] {e}")
        bot.send_message(msg.chat.id, "کاتالوگ آماده‌ست! بگو چی دوست داری تا نمونه بفرستم.")
    bot.send_message(msg.chat.id, "برگشت به منو:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "✂️ برش بهینه")
def cut_optimize(msg):
    user_state[msg.chat.id] = "cut_stock"
    bot.send_message(msg.chat.id, "✂️ برش بهینه شروع شد!\n\nابتدا ابعاد ورق اصلی رو بفرست (به cm):\nمثال: 183x366")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) in ["cut_stock", "cut_parts"])
def cut_handler(msg):
    cid = msg.chat.id
    state = user_state[cid]

    if state == "cut_stock":
        try:
            w, h = map(float, msg.text.split('x'))
            user_data[cid] = {"stock": (w, h), "parts": []}
            bot.send_message(cid, f"ورق اصلی ثبت شد: {w}×{h} cm ✅\n\nحالا ابعاد قطعات رو یکی یکی بفرست:\nمثال: 100x50\nوقتی تموم شد بنویس: تمام")
            user_state[cid] = "cut_parts"
        except:
            bot.send_message(cid, "فرمت اشتباه! مثال: 183x366")

    elif state == "cut_parts":
        if msg.text.lower() == "تمام":
            # اینجا بعداً نقشه واقعی می‌فرستیم
            bot.send_message(cid, "در حال محاسبه برش بهینه...\nبه زودی نقشه واقعی و درصد پرتی رو می‌فرستم 🛠️\n(نسخه کامل به زودی اضافه می‌شه)")
            del user_data[cid]
            user_state.pop(cid, None)
            bot.send_message(cid, "چیزی دیگه نیاز داری؟", reply_markup=main_menu())
        else:
            try:
                w, h = map(float, msg.text.split('x'))
                user_data[cid]["parts"].append((w, h))
                bot.send_message(cid, f"قطعه {w}×{h} اضافه شد ✅\nقطعه بعدی یا 'تمام'")
            except:
                bot.send_message(cid, "فرمت اشتباه! مثال: 100x50")
    # ادامه در chat handler

@bot.message_handler(func=lambda m: m.text == "📞 تماس با من")
def contact_me(msg):
    try:
        with open(IMG_PATH / "contact.jpg", "rb") as photo:  # عکس تماس اگر داری
            bot.send_photo(
                msg.chat.id,
                photo,
                caption=(
                    "📞 برای مشاوره مستقیم و سریع با من در ارتباط باش:\n\n"
                    f"تلگرام: {ADMIN_TELEGRAM}\n"
                    f"شماره تلفن: {ADMIN_PHONE}\n\n"
                    "هر سوالی داری، پیام بده یا زنگ بزن — همیشه در خدمتم 🛠️😊"
                ),
                reply_markup=main_menu()
            )
    except Exception as e:
        log.error(f"[Contact Photo Error] {e}")
        bot.send_message(
            msg.chat.id,
            (
                "📞 برای مشاوره مستقیم با من در ارتباط باش:\n\n"
                f"تلگرام: {ADMIN_TELEGRAM}\n"
                f"شماره تلفن: {ADMIN_PHONE}\n\n"
                "هر سوالی داری، پیام بده یا زنگ بزن — همیشه در خدمتم 🛠️😊"
            ),
            reply_markup=main_menu()
        )

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
        log.error(f"[Hossein Photo Error] {e}")
        bot.send_message(
            msg.chat.id,
            "سلام! من حسین تراب‌پرورم 🛠️\n"
            "۱۵ سال تجربه دارم و آماده‌ام کمکت کنم.\n"
            "سوالت چیه؟"
        )

# General Chat Handler
@bot.message_handler(func=lambda m: True)
def chat(msg):
    state = user_state.get(msg.chat.id)

    if state == "digital_hossein":
        try:
            reply = h_agent.generate_response(msg.text)
            bot.send_message(msg.chat.id, reply)
        except Exception as e:
            log.error(f"[H Agent Error] {e}")
            bot.send_message(msg.chat.id, "متاسفانه نسخه دیجیتال الان در دسترس نیست 😔 دوباره امتحان کن.")
        # ادامه چت
        bot.register_next_step_handler_by_chat_id(msg.chat.id, chat)

    elif state == "quick_ai":
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": msg.text}]
            )
            bot.send_message(msg.chat.id, response.choices[0].message.content)
        except Exception as e:
            bot.send_message(msg.chat.id, "خطا در هوش مصنوعی — دوباره امتحان کن.")

    elif state == "order":
        bot.send_message(msg.chat.id, "سفارشت ثبت شد! به زودی تماس می‌گیرم 🙏", reply_markup=main_menu())
        user_state.pop(msg.chat.id, None)  # پایان حالت سفارش

    elif state == "cut":
        bot.send_message(msg.chat.id, "در حال توسعه برش بهینه پیشرفته... به زودی نقشه واقعی اضافه می‌شه!")

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
    return "بات نجاری حسین تراب‌پرور آنلاینه 🛠️"

if __name__ == "__main__":
    log.info("بات نجاری حسین تراب‌پرور در حال اجراست...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




