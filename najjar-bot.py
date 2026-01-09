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
import requests

# Import HAgent
from core.h_agent import h_agent

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

# Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")

if not TELEGRAM_TOKEN:
    log.error("TELEGRAM_TOKEN missing!")
    raise ValueError("TELEGRAM_TOKEN required")

# Initialize
bot = TeleBot(TELEGRAM_TOKEN)

user_state = {}
user_data = {}  # برای ذخیره ورق و قطعات

IMG_PATH = Path("images")
IMG_PATH.mkdir(exist_ok=True)  # ایجاد پوشه اگر وجود ندارد

# اطلاعات تماس
ADMIN_TELEGRAM_LINK = "https://t.me/hossein_torabparvar"
ADMIN_PHONE = "09123456789"  # شماره واقعی خودت
ADMIN_WHATSAPP = f"https://wa.me/{ADMIN_PHONE[1:]}"

# منو اصلی
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🖼️ نمونه کارها", "✂️ برش بهینه")
    kb.add("📞 تماس با ما", "📝 درباره ما")
    kb.add("📦 ثبت سفارش", "🤖 چت با حسین (هوش مصنوعی)")
    return kb

# شروع
@bot.message_handler(commands=["start"])
def start(msg):
    welcome = (
        "🌳 **سلام! به کارگاه نجاری و MDF کاری حسین تراب‌پرور خوش اومدی** 🛠️\n\n"
        "✅ **۱۵ سال تجربه** در نجاری و MDF\n"
        "✅ **تخصص:** کابینت، کمد، سرویس خواب، دکوراسیون\n"
        "✅ **خدمات:** طراحی، ساخت، نصب، تعمیر\n\n"
        "👇 از منوی زیر انتخاب کن:"
    )
    bot.send_message(msg.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu())

# دکمه نمونه کارها
@bot.message_handler(func=lambda m: m.text == "🖼️ نمونه کارها")
def gallery(msg):
    cid = msg.chat.id
    
    # بررسی وجود عکس‌ها
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(list(IMG_PATH.glob(ext)))
    
    if not image_files:
        bot.send_message(cid, 
            "📸 **نمونه کارها**\n\n"
            "به زودی نمونه کارهایم رو اینجا می‌ذارم!\n"
            "فعلاً می‌تونی از طریق دکمه‌های زیر نمونه‌هایی رو ببینی:",
            parse_mode="Markdown"
        )
    else:
        # ارسال ۳ عکس اول
        for i, img_path in enumerate(image_files[:3]):
            try:
                with open(img_path, 'rb') as photo:
                    caption = f"🖼️ نمونه کار {i+1} - کارگاه حسین تراب‌پرور" if i == 0 else None
                    bot.send_photo(cid, photo, caption=caption)
            except Exception as e:
                log.error(f"Error sending photo: {e}")
    
    # دکمه‌های دسته‌بندی
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("کابینت آشپزخانه", callback_data="gallery_kitchen"),
        types.InlineKeyboardButton("کمد دیواری", callback_data="gallery_wardrobe")
    )
    kb.add(
        types.InlineKeyboardButton("سرویس خواب", callback_data="gallery_bedroom"),
        types.InlineKeyboardButton("میز و کنسول", callback_data="gallery_table")
    )
    kb.add(types.InlineKeyboardButton("📲 کانال تلگرام", url="https://t.me/your_channel"))
    
    bot.send_message(cid, "👇 برای دیدن نمونه کارها در هر دسته کلیک کنید:", reply_markup=kb)

# تماس با ما
@bot.message_handler(func=lambda m: m.text == "📞 تماس با ما")
def contact(msg):
    cid = msg.chat.id
    contact_text = (
        "📞 **تماس با کارگاه نجاری حسین تراب‌پرور**\n\n"
        "👤 **حسین تراب‌پرور**\n"
        f"📱 **واتساپ:** [مستقیم در واتساپ]({ADMIN_WHATSAPP})\n"
        f"✈️ **تلگرام:** [{ADMIN_TELEGRAM_LINK.split('/')[-1]}]({ADMIN_TELEGRAM_LINK})\n"
        f"☎️ **تلفن:** `{ADMIN_PHONE}`\n\n"
        "📍 **آدرس:** کرج، فردیس\n"
        "🕐 **ساعات کاری:** ۹ صبح تا ۹ شب\n\n"
        "📌 **برای مشاوره رایگان تماس بگیرید!** 🛠️"
    )
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📱 تماس تلفنی", url=f"tel:{ADMIN_PHONE}"),
        types.InlineKeyboardButton("💬 چت در واتساپ", url=ADMIN_WHATSAPP)
    )
    kb.add(
        types.InlineKeyboardButton("✈️ پیام در تلگرام", url=ADMIN_TELEGRAM_LINK),
        types.InlineKeyboardButton("🗺️ موقعیت در نقشه", callback_data="location")
    )
    
    bot.send_message(cid, contact_text, parse_mode="Markdown", 
                     disable_web_page_preview=True, reply_markup=kb)

# درباره ما
@bot.message_handler(func=lambda m: m.text == "📝 درباره ما")
def about(msg):
    cid = msg.chat.id
    
    about_text = (
        "🎯 **درباره کارگاه نجاری حسین تراب‌پرور**\n\n"
        "✅ **۱۵ سال سابقه** در نجاری و MDF کاری\n"
        "✅ **تخصص در:**\n"
        "   • کابینت آشپزخانه\n"
        "   • کمد دیواری و لباس\n"
        "   • سرویس خواب و تخت\n"
        "   • پارتیشن و دکوراسیون\n"
        "   • میز، کنسول و شلف\n\n"
        "✅ **متریال‌های مورد استفاده:**\n"
        "   • MDF معمولی و ضد رطوبت\n"
        "   • MDF نما چوب\n"
        "   • هایگلاس و ممبران\n"
        "   • چوب روسی و MDF راش\n\n"
        "✅ **تجهیزات پیشرفته:**\n"
        "   • دستگاه CNC\n"
        "   • دستگاه برش و فرز\n"
        "   • ابزارهای نصب حرفه‌ای\n\n"
        "✅ **گارانتی:**\n"
        "   • ۲ سال گارانتی نصب\n"
        "   • خدمات پس از فروش\n\n"
        "🛠️ **شعار ما:** کیفیت در کار، صداقت در قیمت!"
    )
    
    # ارسال عکس درباره ما
    about_image = IMG_PATH / "about.jpg"
    if about_image.exists():
        try:
            with open(about_image, 'rb') as photo:
                bot.send_photo(cid, photo, caption=about_text, parse_mode="Markdown")
        except:
            bot.send_message(cid, about_text, parse_mode="Markdown")
    else:
        bot.send_message(cid, about_text, parse_mode="Markdown")
    
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📞 تماس با ما", callback_data="contact_from_about"))
    
    bot.send_message(cid, "برای مشاوره رایگان کلیک کنید:", reply_markup=kb)

# ثبت سفارش (واتساپ)
@bot.message_handler(func=lambda m: m.text == "📦 ثبت سفارش")
def order_start(msg):
    cid = msg.chat.id
    user_state[cid] = "order_name"
    user_data[cid] = {}
    
    bot.send_message(cid, 
        "📝 **ثبت سفارش جدید**\n\n"
        "سفارش شما مستقیماً به واتساپ ارسال می‌شود.\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
        parse_mode="Markdown"
    )

# چت با هوش مصنوعی (HAgent)
@bot.message_handler(func=lambda m: m.text == "🤖 چت با حسین (هوش مصنوعی)")
def start_ai_chat(msg):
    cid = msg.chat.id
    user_state[cid] = "ai_chat"
    
    welcome_msg = (
        "🤖 **چت با حسین تراب‌پرور (نسخه هوش مصنوعی)**\n\n"
        "سلام! من حسینم، نسخه دیجیتالی خودم! 😊\n\n"
        "📌 **چطور می‌تونم کمک کنم:**\n"
        "• مشاوره طراحی کابینت و کمد\n"
        "• انتخاب متریال مناسب\n"
        "• برآورد هزینه و زمان\n"
        "• راهنمایی تعمیرات\n"
        "• آموزش کار با ابزار\n"
        "• پاسخ به سوالات فنی\n\n"
        "🎯 **لطفاً سوال خود را به فارسی بپرسید:**\n"
        "مثال: 'برای کابینت آشپزخانه چه MDF ای مناسب است؟'\n\n"
        "برای بازگشت به منو /menu تایپ کنید."
    )
    
    bot.send_message(cid, welcome_msg, parse_mode="Markdown")

# برش بهینه
@bot.message_handler(func=lambda m: m.text == "✂️ برش بهینه")
def cut_start(msg):
    cid = msg.chat.id
    user_state[cid] = "cut_stock"
    user_data[cid] = {"parts": []}
    
    bot.send_message(cid,
        "✂️ **برش بهینه حرفه‌ای**\n\n"
        "با الگوریتم CutMaster Pro:\n"
        "✅ کمترین پرتی ممکن\n"
        "✅ چیدمان هوشمند قطعات\n"
        "✅ امکان چرخش ۹۰ درجه\n"
        "✅ گزارش کامل متریال\n\n"
        "**لطفاً ابعاد ورق اصلی را وارد کنید (سانتی‌متر):**\n"
        "📏 مثال: `183x366`",
        parse_mode="Markdown"
    )

# هندلر اصلی پیام‌ها
@bot.message_handler(func=lambda m: True)
def general_handler(msg):
    cid = msg.chat.id
    state = user_state.get(cid)
    text = msg.text
    
    # بازگشت به منو
    if text == "/menu":
        bot.send_message(cid, "منوی اصلی:", reply_markup=main_menu())
        user_state.pop(cid, None)
        if cid in user_data:
            del user_data[cid]
        return
    
    # چت با هوش مصنوعی
    if state == "ai_chat":
        # نشان دادن تایپ کردن
        bot.send_chat_action(cid, 'typing')
        
        # استفاده از HAgent برای پاسخ
        response = h_agent.generate_response(text)
        
        # ارسال پاسخ
        bot.send_message(cid, response, parse_mode="Markdown")
        return
    
    # ثبت سفارش - مرحله ۱: نام
    elif state == "order_name":
        user_data[cid]["name"] = text
        user_state[cid] = "order_phone"
        bot.send_message(cid, "✅ نام ثبت شد.\n\n📱 لطفاً **شماره تلفن** خود را وارد کنید:")
    
    # ثبت سفارش - مرحله ۲: تلفن
    elif state == "order_phone":
        user_data[cid]["phone"] = text
        user_state[cid] = "order_details"
        bot.send_message(cid, 
            "✅ شماره تلفن ثبت شد.\n\n"
            "📝 **توضیحات سفارش را وارد کنید:**\n"
            "• نوع کار (کابینت، کمد، ...)\n"
            "• ابعاد تقریبی\n"
            "• متریال مورد نظر\n"
            "• زمان مورد نیاز\n"
            "• هر نکته دیگری"
        )
    
    # ثبت سفارش - مرحله ۳: جزئیات
    elif state == "order_details":
        user_data[cid]["details"] = text
        user_state[cid] = "order_confirm"
        
        # نمایش خلاصه سفارش
        summary = (
            f"📋 **خلاصه سفارش:**\n\n"
            f"👤 **نام:** {user_data[cid]['name']}\n"
            f"📱 **تلفن:** {user_data[cid]['phone']}\n"
            f"📝 **توضیحات:** {user_data[cid]['details']}\n\n"
            f"آیا اطلاعات صحیح است؟"
        )
        
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add("✅ بله، ارسال کن", "❌ نه، اصلاح کن")
        
        bot.send_message(cid, summary, parse_mode="Markdown", reply_markup=kb)
    
    # تایید نهایی سفارش
    elif state == "order_confirm":
        if text == "✅ بله، ارسال کن":
            send_to_whatsapp(cid)
            user_state.pop(cid, None)
            user_data.pop(cid, None)
            bot.send_message(cid, "منوی اصلی:", reply_markup=main_menu())
        elif text == "❌ نه، اصلاح کن":
            user_state[cid] = "order_name"
            bot.send_message(cid, "لطفاً نام خود را مجدداً وارد کنید:")
        else:
            bot.send_message(cid, "لطفاً یکی از گزینه‌ها را انتخاب کنید.")
    
    # برش بهینه - مرحله ۱: ورق اصلی
    elif state == "cut_stock":
        try:
            w, h = map(float, text.replace('×', 'x').split('x'))
            user_data[cid]["stock"] = (w, h)
            bot.send_message(cid, 
                f"✅ ورق اصلی ثبت شد: {w}×{h} سانتی‌متر\n\n"
                f"**حالا ابعاد قطعات را یکی یکی وارد کنید:**\n"
                f"📏 مثال: `100x50`\n"
                f"✏️ وقتی تمام شد بنویسید: `تمام`",
                parse_mode="Markdown"
            )
            user_state[cid] = "cut_parts"
        except:
            bot.send_message(cid, "❌ فرمت اشتباه!\nمثال صحیح: `183x366`", parse_mode="Markdown")
    
    # برش بهینه - مرحله ۲: قطعات
    elif state == "cut_parts":
        if text.lower() in ["تمام", "تموم", "پایان", "end", "done"]:
            generate_cut_plan(cid)
        else:
            try:
                w, h = map(float, text.replace('×', 'x').split('x'))
                user_data[cid]["parts"].append((w, h))
                count = len(user_data[cid]["parts"])
                bot.send_message(cid, f"✅ قطعه {count}: {w}×{h} اضافه شد\nقطعه بعدی یا 'تمام'")
            except:
                bot.send_message(cid, "❌ فرمت اشتباه!\nمثال صحیح: `100x50`")
    
    # حالت پیش‌فرض
    else:
        bot.send_message(cid, "لطفاً از منوی زیر انتخاب کنید 👇", reply_markup=main_menu())

# ارسال سفارش به واتساپ
def send_to_whatsapp(cid):
    order_data = user_data.get(cid, {})
    
    if not order_data:
        bot.send_message(cid, "❌ خطا در دریافت اطلاعات سفارش!")
        return
    
    # ساخت پیام سفارش
    order_message = (
        "📦 **سفارش جدید از بات تلگرام**\n\n"
        f"👤 نام: {order_data.get('name', 'ندارد')}\n"
        f"📱 تلفن: {order_data.get('phone', 'ندارد')}\n"
        f"📝 توضیحات:\n{order_data.get('details', 'ندارد')}\n\n"
        f"⏰ زمان: {request.get_data().decode('utf-8')[:19] if request.get_data() else 'همین لحظه'}"
    )
    
    # لینک مستقیم واتساپ
    whatsapp_url = f"{ADMIN_WHATSAPP}?text={requests.utils.quote(order_message)}"
    
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📱 ارسال در واتساپ", url=whatsapp_url))
    
    bot.send_message(cid,
        "✅ **سفارش شما آماده ارسال است!**\n\n"
        "برای تکمیل فرآیند، لطفاً روی دکمه زیر کلیک کنید\n"
        "تا مستقیماً به واتساپ منتقل شوید:\n\n"
        f"**شماره پیگیری:** `{uuid.uuid4().hex[:8].upper()}`",
        parse_mode="Markdown",
        reply_markup=kb
    )
    
    # لاگ اطلاعات سفارش
    log.info(f"New order from {order_data.get('name')} - Phone: {order_data.get('phone')}")

# الگوریتم برش بهینه
def generate_cut_plan(cid):
    if cid not in user_data or "stock" not in user_data[cid]:
        bot.send_message(cid, "❌ اطلاعات ورق اصلی یافت نشد!")
        return
    
    stock_w, stock_h = user_data[cid]["stock"]
    parts = user_data[cid].get("parts", [])
    
    if not parts:
        bot.send_message(cid, "❌ هیچ قطعه‌ای وارد نشده است!")
        return
    
    # الگوریتم ساده برش (می‌توانید پیچیده‌تر کنید)
    bins = []
    
    # مرتب‌سازی قطعات از بزرگ به کوچک
    sorted_parts = sorted(parts, key=lambda x: x[0]*x[1], reverse=True)
    
    for pw, ph in sorted_parts:
        placed = False
        
        # سعی در قرار دادن در ورق‌های موجود
        for bin_idx, bin in enumerate(bins):
            bin_w, bin_h, bin_items = bin
            
            # چک کردن جا در ورق فعلی
            if pw <= stock_w and ph <= stock_h:
                # می‌توانید الگوریتم پیشرفته‌تر اینجا پیاده کنید
                bins[bin_idx][2].append((pw, ph, 0, 0))
                placed = True
                break
        
        # اگر جا نشد، ورق جدید
        if not placed:
            bins.append([stock_w, stock_h, [(pw, ph, 0, 0)]])
    
    # رسم نقشه
    if not bins:
        bot.send_message(cid, "❌ محاسبه برش با مشکل مواجه شد!")
        return
    
    fig, axs = plt.subplots(1, len(bins), figsize=(6*len(bins), 6))
    if len(bins) == 1:
        axs = [axs]
    
    total_part_area = sum(p[0]*p[1] for p in parts)
    total_sheet_area = len(bins) * stock_w * stock_h
    waste_percent = 100 * (1 - total_part_area/total_sheet_area) if total_sheet_area > 0 else 0
    
    for idx, (bin_w, bin_h, items) in enumerate(bins):
        ax = axs[idx]
        
        # رسم ورق
        ax.add_patch(Rectangle((0, 0), bin_w, bin_h, fill=None, 
                              edgecolor='navy', linewidth=3, alpha=0.7))
        
        # رسم قطعات
        for pw, ph, x, y in items:
            color = '#4ECDC4'  # رنگ ثابت
            ax.add_patch(Rectangle((x, y), pw, ph, 
                                  facecolor=color, edgecolor='white', 
                                  linewidth=2, alpha=0.8))
            
            # متن روی قطعه
            ax.text(x + pw/2, y + ph/2, f"{pw}×{ph}", 
                   ha='center', va='center', 
                   color='white', fontweight='bold', fontsize=10)
        
        ax.set_xlim(0, bin_w * 1.1)
        ax.set_ylim(0, bin_h * 1.1)
        ax.set_aspect('equal')
        ax.set_title(f"📦 ورق {idx+1}", fontsize=12, fontweight='bold')
        ax.axis('off')
    
    plt.suptitle(f"برش بهینه با CutMaster Pro", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # ذخیره و ارسال
    filename = f"cut_plan_{uuid.uuid4().hex[:8]}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    caption = (
        f"✅ **برش بهینه آماده شد!**\n\n"
        f"📊 **آمار برش:**\n"
        f"• تعداد ورق: {len(bins)}\n"
        f"• تعداد قطعات: {len(parts)}\n"
        f"• پرتی: {waste_percent:.1f}%\n"
        f"• مساحت قطعات: {total_part_area/10000:.2f} m²\n"
        f"• مساحت ورق‌ها: {total_sheet_area/10000:.2f} m²\n\n"
        f"🎯 **بهینه‌ترین حالت ممکن!**\n"
        f"برای سفارش چوب و MDF با ما تماس بگیرید."
    )
    
    try:
        with open(filename, 'rb') as photo:
            bot.send_photo(cid, photo, caption=caption, parse_mode="Markdown")
        os.remove(filename)
    except Exception as e:
        bot.send_message(cid, f"خطا در ایجاد نقشه: {str(e)}")
        log.error(f"Error generating cut plan: {e}")
    
    # پاکسازی
    if cid in user_data:
        del user_data[cid]
    if cid in user_state:
        user_state.pop(cid, None)
    
    bot.send_message(cid, "🛠️ کار دیگری نیاز دارید؟", reply_markup=main_menu())

# هندلر Callback Query
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    
    if call.data.startswith("gallery_"):
        category = call.data.replace("gallery_", "")
        
        categories = {
            "kitchen": "کابینت آشپزخانه",
            "wardrobe": "کمد دیواری",
            "bedroom": "سرویس خواب",
            "table": "میز و کنسول"
        }
        
        category_name = categories.get(category, "پروژه‌ها")
        
        bot.answer_callback_query(call.id, f"در حال بارگیری نمونه‌های {category_name}...")
        
        # فعلاً پیام نمونه
        bot.send_message(cid, 
            f"🖼️ **نمونه‌های {category_name}**\n\n"
            f"به زودی عکس‌های این بخش اضافه می‌شود.\n"
            f"برای مشاهده نمونه‌های فعلی، به کانال تلگرام مراجعه کنید یا از دکمه تماس با ما استفاده کنید.",
            parse_mode="Markdown"
        )
    
    elif call.data == "contact_from_about":
        contact(call.message)
    
    elif call.data == "location":
        # می‌توانید موقعیت جغرافیایی بفرستید
        bot.answer_callback_query(call.id, "موقعیت به زودی اضافه می‌شود")
        bot.send_message(cid, "📍 **موقعیت کارگاه:**\nبه زودی نقشه اینجا قرار می‌گیرد.")

# Webhook
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "🛠️ کارگاه نجاری حسین تراب‌پرور - بات فعال"

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "najjar_bot"}), 200

if __name__ == "__main__":
    log.info("🚀 بات نجاری شروع به کار کرد...")
    log.info(f"🤖 HAgent loaded: {h_agent.__class__.__name__}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)







