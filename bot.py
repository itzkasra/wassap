import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8966095989:AAECkTerajVQZGccb2fVlQVasaGODAZIrZA"
ADMIN_IDS = [5231145229, 7513168976] 
OWNER_ID = 5231145229
CHANNEL_USERNAME = "@v2rayng_tornado"
CHANNEL_LINK = "https://t.me/v2rayng_tornado"
CARD = "6219861816124019"
CARD_NAME = "عبداله وند"

# قیمت‌ها بر اساس حجم (GB)
PRICES = {
    1: 250,
    2: 455,
    3: 700,
    4: 950,
    5: 1200,
    10: 2300,
    20: 4600
}

user_data = {}
user_messages = {}
DIVIDER = "━━━━━━━━━━━━━━"

# ================= DATABASE =================

# اصلاح مسیر دیتابیس برای سرور
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'v2ray_bot.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

init_db()

# ================= FUNCTIONS =================

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

RULES_TEXT = f"""
<b>📜 قوانین و مقررات استفاده از سرویس</b>
{DIVIDER}

۱ — استفاده از سرویس‌ها صرفاً برای <b>مصرف شخصی</b> می‌باشد. در صورت استفاده تجاری یا پخش اکانت، دسترسی شما بدون بازگشت وجه <b>مسدود</b> خواهد شد. ⚠️🚫

۲ — به دلیل شرایط شبکه، سرویس‌ها دارای <b>تضمین دائمی</b> نمی‌باشند اما ما همیشه برای پایداری تلاش می‌کنیم. 🌍❌

۳ — سرویس‌ها محدود هستند و امکان ارائه اکانت تست وجود ندارد. 🔒🙅‍♂️

{DIVIDER}
با زدن دکمه <b>"✅ می‌پذیرم"</b> تأیید می‌کنی که قوانین را خوانده‌ای.
"""

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    add_user(user_id)
    
    if not await is_member(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]]
        await update.message.reply_text(f"<b>⚠️ برای استفاده باید عضو کانال باشی:</b>\n\n{DIVIDER}",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
    await update.message.reply_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await is_member(context.bot, q.from_user.id):
        await q.answer("✅ عضویت تایید شد!")
        keyboard = [[InlineKeyboardButton("✅ می‌پذیرم", callback_data="accept_rules")]]
        await q.edit_message_text(RULES_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await q.answer("❌ هنوز عضو کانال نشدی!", show_alert=True)

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 خرید سرویس VIP", callback_data="go_plans")],
        [InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/iranbiubiuvip"), InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)]
    ]
    text = f"<b>🏠 به ربات V2rayNG Tornado خوش آمدی</b>\n\n{DIVIDER}\nلطفاً برای ادامه انتخاب کنید:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    keyboard = []
    for gb, price in PRICES.items():
        keyboard.append([InlineKeyboardButton(f"💎 سرویس {gb} گیگابایت ({price:,}T)", callback_data=f"sel_{gb}")])
    
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="home")])
    
    await q.edit_message_text(f"<b>💎 انتخاب حجم سرویس VIP</b>\n{DIVIDER}\nلطفاً حجم مورد نظر خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    gb = q.data.split("_")[1]
    
    keyboard = []
    row = []
    for i in range(1, 6): # انتخاب از ۱ تا ۵ عدد
        row.append(InlineKeyboardButton(f"{i} عدد", callback_data=f"qty_{gb}_{i}"))
    keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="go_plans")])
    
    await q.edit_message_text(f"<b>🔢 تعداد اکانت</b>\n{DIVIDER}\nشما حجم <b>{gb} گیگ</b> را انتخاب کردید.\nچه تعداد از این اکانت نیاز دارید؟", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def order_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, gb, qty = q.data.split("_")
    gb, qty = int(gb), int(qty)
    
    total_price = PRICES[gb] * qty
    user_data[q.from_user.id] = {"gb": gb, "qty": qty, "total": total_price}
    
    invoice_text = (
        f"<b>📦 فاکتور نهایی خرید</b>\n"
        f"{DIVIDER}\n"
        f"🌟 نوع سرویس: VIP\n"
        f"📊 حجم هر اکانت: {gb} گیگابایت\n"
        f"🔢 تعداد: {qty} عدد\n"
        f"💰 مبلغ کل: <b>{total_price:,} تومان</b>\n\n"
        f"💳 شماره کارت (برای کپی کلیک کنید):\n"
        f"<code>{CARD}</code>\n"
        f"👤 بنام: <b>{CARD_NAME}</b>\n\n"
        f"⚠️ <b>توضیحات مهم:</b>\n"
        f"بعد از پرداخت، حتماً عکس فیش را اینجا ارسال کنید.\n"
        f"برای تمدید فقط به خود ما پیام دهید و مراقب کلاهبرداران باشید. هرگونه واریز به حساب دیگران بر عهده خودتان است.\n\n"
        f"📸 منتظر ارسال رسید شما هستیم..."
    )
    
    await q.edit_message_text(invoice_text, parse_mode="HTML")

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if is_admin(user_id): return
    
    data = user_data.get(user_id)
    if not data:
        await update.message.reply_text("❌ ابتدا از منوی خرید، سرویس خود را انتخاب کنید.")
        return

    gb, qty, total = data["gb"], data["qty"], data["total"]

    for admin in ADMIN_IDS:
        try:
            # فوروارد مستقیم پیام برای ادمین (حاوی اطلاعات فرستنده)
            sent = await context.bot.forward_message(chat_id=admin, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
            
            # ذخیره در حافظه موقت
            user_messages[sent.message_id] = user_id
            
            admin_msg = (
                f"🧾 <b>رسید پرداخت جدید</b>\n"
                f"{DIVIDER}\n"
                f"👤 کاربر: <code>{user_id}</code>\n"
                f"💎 سرویس: VIP | {gb}GB\n"
                f"🔢 تعداد: {qty} عدد\n"
                f"💰 مبلغ: {total:,} تومان\n\n"
                f"📥 برای پاسخ، روی <b>همین پیام</b> ریپلای کنید."
            )
            await context.bot.send_message(chat_id=admin, text=admin_msg, parse_mode="HTML")
        except: continue
    
    await update.message.reply_text("✅ رسید شما دریافت شد و برای ادمین‌ها ارسال گردید.\nپس از تایید، سرویس شما ارسال خواهد شد.")

# ================= هوشمندسازی پاسخ ادمین =================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id
    if not is_admin(admin_id):
        return

    # چک کردن اینکه ادمین حتماً روی پیامی ریپلای کرده باشد
    if not update.message.reply_to_message:
        return

    replied_msg = update.message.reply_to_message
    target_user = None

    # ۱. جستجو در حافظه موقت ربات
    if replied_msg.message_id in user_messages:
        target_user = user_messages[replied_msg.message_id]
    
    # ۲. اگر ریپلای روی پیام فوروارد شده باشد
    elif replied_msg.forward_from:
        target_user = replied_msg.forward_from.id
    
    # ۳. جستجوی آیدی عددی در متن پیام (اگر حافظه پاک شده باشد)
    elif replied_msg.text and "کاربر:" in replied_msg.text:
        try:
            # استخراج آیدی از متن "کاربر: 123456"
            target_user = int(replied_msg.text.split("کاربر:")[1].split("\n")[0].strip())
        except: pass

    if target_user:
        msg_text = update.message.text
        try:
            await context.bot.send_message(chat_id=target_user, text=f"<b>📩 پاسخ پشتیبانی:</b>\n\n{msg_text}", parse_mode="HTML")
            await update.message.reply_text(f"✅ پیام با موفقیت به مشتری ({target_user}) ارسال شد.")
            
            # ارسال لاگ برای مالک اصلی اگر ادمین دیگری جواب داده بود
            if admin_id != OWNER_ID:
                await context.bot.send_message(chat_id=OWNER_ID, text=f"👮‍♂️ پاسخ ادمین {admin_id} به {target_user}:\n\n{msg_text}")
        except Exception as e:
            await update.message.reply_text(f"❌ ارسال نشد. احتمالاً کاربر ربات را بلاک کرده است.\nخطا: {e}")
    else:
        await update.message.reply_text("❌ آیدی مشتری پیدا نشد. لطفاً آیدی عددی کاربر را در متن ریپلای بنویسید یا مجدد تلاش کنید.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("❌ مثال: /send سلام")
        return
    text = " ".join(context.args)
    users = get_all_users()
    done, fail = 0, 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>اطلاعیه</b>\n\n{text}", parse_mode="HTML")
            done += 1
        except: fail += 1
    await update.message.reply_text(f"✅ ارسال همگانی پایان یافت.\nموفق: {done} | ناموفق: {fail}")

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", broadcast))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(home, pattern="accept_rules|home"))
app.add_handler(CallbackQueryHandler(select_plan, pattern="go_plans"))
app.add_handler(CallbackQueryHandler(select_quantity, pattern="sel_"))
app.add_handler(CallbackQueryHandler(order_invoice, pattern="qty_"))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_handler))
# فیلتر کردن متن‌ها برای پاسخ ادمین
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply))

print("V2rayNG Tornado Bot is running...")
app.run_polling()
