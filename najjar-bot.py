from dotenv import load_dotenv
load_dotenv()

import os
import logging
from pathlib import Path
from flask import Flask, request
from telebot import TeleBot, types
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import uuid

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

# Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    log.error("TELEGRAM_TOKEN missing!")
    raise ValueError("TELEGRAM_TOKEN required")

# Initialize
bot = TeleBot(TELEGRAM_TOKEN)

user_state = {}
user_data = {}  # برای ذخیره ورق و قطعات
IMG_PATH = Path("images")

# اطلاعات تماس
ADMIN_TELEGRAM_LINK = "https://t.me/hossein_torabparvar"  # لینک واقعی خودت
ADMIN_PHONE = "09123456789"  # شماره واقعی خودت

# منو اصلی
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📋 کاتالوگ", "✂️ برش بهینه")
    kb.add("📞 تماس با من", "📦 ثبت سفارش")
    kb.add("💻 نسخه دیجیتال حسین")
    return kb

# شروع
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🌳 سلام! به کارگاه حسین تراب‌پرور خوش اومدی 🛠️\n"
        "۱۵ سال تجربه نجاری و MDF دارم\n"
        "از منوی زیر انتخاب کن:",
        reply_markup=main_menu()
    )

# دکمه‌ها
@bot.message_handler(func=lambda m: m.text == "📋 کاتالوگ")
def catalog(msg):
    bot.send_message(msg.chat.id, "📸 کاتالوگ کارهایم آماده‌ست!\nبگو چی دوست داری تا نمونه بفرستم.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📞 تماس با من")
def contact(msg):
    bot.send_message(
        msg.chat.id,
        f"📞 تماس مستقیم با من:\n\n"
        f"تلگرام: {ADMIN_TELEGRAM_LINK}\n"
        f"شماره: {ADMIN_PHONE}\n\n"
        f"کلیک کن روی لینک، مستقیم وارد چت می‌شی 🛠️",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📦 ثبت سفارش")
def order(msg):
    user_state[msg.chat.id] = "order"
    bot.send_message(msg.chat.id, "نام، شماره و توضیحات سفارش رو بنویس.\nبه زودی تماس می‌گیرم.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💻 نسخه دیجیتال حسین")
def digital_hossein(msg):
    user_state[msg.chat.id] = "digital"
    bot.send_message(
        msg.chat.id,
        "💻 نسخه دیجیتال حسین تراب‌پرور فعال شد!\n\n"
        "سلام! منم حسین، ولی نسخه دیجیتالش 😊\n"
        "هر سوالی بپرس — کابینت، تعمیر، ابزار، هزینه...\n"
        "بگو چی می‌خوای؟ 🛠️",
        reply_markup=main_menu()
    )

# برش بهینه — شروع
@bot.message_handler(func=lambda m: m.text == "✂️ برش بهینه")
def cut_start(msg):
    user_state[msg.chat.id] = "cut_stock"
    user_data[msg.chat.id] = {"parts": []}
    bot.send_message(msg.chat.id, "✂️ برش بهینه پیشرفته شروع شد!\n\nابعاد ورق اصلی رو بفرست (cm):\nمثال: 183x366")

# هندلر عمومی — شامل برش بهینه کامل
@bot.message_handler(func=lambda m: True)
def general_handler(msg):
    cid = msg.chat.id
    state = user_state.get(cid)

    if state == "digital":
        # نسخه دیجیتال (اگر بخوای بعداً اضافه کنی)
        bot.send_message(cid, "نسخه دیجیتال در حال توسعه است... به زودی با هوش مصنوعی جواب می‌دم!")

    elif state == "cut_stock":
        try:
            w, h = map(float, msg.text.split('x'))
            user_data[cid]["stock"] = (w, h)
            bot.send_message(cid, f"ورق اصلی ثبت شد: {w}×{h} cm ✅\n\nحالا ابعاد قطعات رو یکی یکی بفرست:\nمثال: 100x50\nوقتی تموم شد بنویس: تمام")
            user_state[cid] = "cut_parts"
        except:
            bot.send_message(cid, "فرمت اشتباه! مثال درست: 183x366")

    elif state == "cut_parts":
        if msg.text.lower() == "تمام":
            generate_cut_plan(cid)
        else:
            try:
                w, h = map(float, msg.text.split('x'))
                user_data[cid]["parts"].append((w, h))
                bot.send_message(cid, f"قطعه {w}×{h} اضافه شد ✅\nقطعه بعدی یا 'تمام'")
            except:
                bot.send_message(cid, "فرمت اشتباه! مثال درست: 100x50")

    elif state == "order":
        bot.send_message(cid, "سفارشت ثبت شد! به زودی تماس می‌گیرم 🙏")
        user_state.pop(cid, None)

    else:
        bot.send_message(cid, "از منو انتخاب کن 👇", reply_markup=main_menu())

# برش بهینه — تولید نقشه واقعی
def generate_cut_plan(cid):
    stock_w, stock_h = user_data[cid]["stock"]
    parts = sorted(user_data[cid]["parts"], key=lambda x: -max(x))  # مرتب‌سازی برای کمترین پرتی

    bins = []  # هر ورق یک bin
    for pw, ph in parts:
        placed = False
        for bin in bins:
            if pw <= bin['remain_w'] and ph <= bin['remain_h']:
                bin['items'].append((pw, ph, bin['used_w'], bin['used_h']))
                bin['used_h'] += ph
                placed = True
                break
            # چرخش 90 درجه
            if ph <= bin['remain_w'] and pw <= bin['remain_h']:
                bin['items'].append((ph, pw, bin['used_w'], bin['used_h']))
                bin['used_h'] += pw
                placed = True
                break
        if not placed:
            bins.append({
                'remain_w': stock_w,
                'remain_h': stock_h,
                'used_w': 0,
                'used_h': 0,
                'items': [(pw, ph, 0, 0)]
            })

    # رسم نقشه با matplotlib
    fig, axs = plt.subplots(1, len(bins), figsize=(6 * len(bins), 6))
    if len(bins) == 1:
        axs = [axs]

    total_area = sum(p[0] * p[1] for p in parts)
    used_area = len(bins) * stock_w * stock_h
    waste = 100 * (1 - total_area / used_area) if used_area > 0 else 0

    for idx, bin in enumerate(bins):
        ax = axs[idx]
        ax.add_patch(Rectangle((0, 0), stock_w, stock_h, fill=None, edgecolor='black', linewidth=3))
        for pw, ph, x, y in bin['items']:
            ax.add_patch(Rectangle((x, y), pw, ph, facecolor='#1E90FF', edgecolor='white', linewidth=2))
            ax.text(x + pw/2, y + ph/2, f"{pw}×{ph}", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        ax.set_xlim(0, stock_w + 10)
        ax.set_ylim(0, stock_h + 10)
        ax.set_aspect('equal')
        ax.set_title(f"ورق {idx+1}", fontsize=14)
        ax.axis('off')

    filename = f"cut_plan_{uuid.uuid4()}.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    caption = (
        f"✂️ نقشه برش بهینه آماده شد!\n\n"
        f"تعداد ورق مصرفی: {len(bins)}\n"
        f"درصد پرتی: {waste:.1f}%\n"
        f"متریال مصرفی: {total_area / 10000:.2f} مترمربع\n"
        f"بهینه‌سازی حرفه‌ای مثل Cut Master Pro!"
    )

    with open(filename, "rb") as photo:
        bot.send_photo(cid, photo, caption=caption)

    os.remove(filename)

    # پاک کردن داده‌ها
    del user_data[cid]
    user_state.pop(cid, None)
    bot.send_message(cid, "چیزی دیگه نیاز داری؟", reply_markup=main_menu())

# Webhook
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "بات حسین تراب‌پرور آنلاینه 🛠️"

if __name__ == "__main__":
    log.info("بات شروع شد...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))






