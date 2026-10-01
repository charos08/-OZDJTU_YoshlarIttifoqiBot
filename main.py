import html
import sqlite3
import time
import telebot
from telebot import types

TOKEN = "8552726928:AAGZEBm_JnhRlqKoiRzMWiaM1dtoIyfklR8"
ADMIN_ID = 6509545133  # Admin Telegram ID raqami

bot = telebot.TeleBot(TOKEN)


# ----------------- MA'LUMOTLAR BAZASI (SQLITE) -----------------
def init_db():
    """Baza va jadvallarni yaratish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            lang TEXT DEFAULT 'uz',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Yangiliklar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id TEXT,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_user(user_id, first_name, username):
    """Yangi foydalanuvchini bazaga qo'shish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (user_id, first_name, username)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            first_name=excluded.first_name,
            username=excluded.username
    """,
        (user_id, first_name, username),
    )
    conn.commit()
    conn.close()


def update_user_lang(user_id, lang):
    """Foydalanuvchi tilini saqlash"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id)
    )
    conn.commit()
    conn.close()


def get_user_lang(user_id):
    """Foydalanuvchi tilini bazadan olish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "uz"


def get_stats():
    """Statistikani olish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users


def get_all_users():
    """Barcha foydalanuvchilar ID larini olish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]


def add_news(photo_id, caption):
    """Yangi yangilik qo'shish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO news (photo_id, caption) VALUES (?, ?)",
        (photo_id, caption),
    )
    conn.commit()
    conn.close()


def get_latest_news():
    """So'nggi yangiliklarni olish"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT photo_id, caption, created_at FROM news ORDER BY id DESC LIMIT 5"
    )
    news_list = cursor.fetchall()
    conn.close()
    return news_list


# Bazani ishga tushiramiz
init_db()

# ----------------- MATNLAR VA MENYU -----------------
TEXTS = {
    "uz": {
        "welcome": "Xush kelibsiz! Kerakli bo'limni tanlang:",
        "menu_1": "ℹ️ Yoshlar Ittifoqi haqida",
        "menu_2": "🏛 O'zDJTU Yoshlar Ittifoqi",
        "menu_3": "👥 Koordinatorlar haqida",
        "menu_4": "📰 Yangilik va e'lonlar",
        "menu_5": "📚 Talabalar uchun",
        "menu_6": "💡 Taklif yuborish",
        "change_lang": "🌐 Tilni o'zgartirish",
        "back": "⬅️️ Ortga",
        "info_yi": (
            "🌟 <b>O‘zbekiston yoshlar ittifoqi haqida</b>\n\n"
            "O‘zbekiston yoshlar ittifoqi — mamlakatimiz yoshlarini har taraflama qo‘llab-quvvatlash, "
            "ularning huquq va manfaatlarini himoya qilish hamda iqtidorini yuzaga chiqarishga xizmat qiladigan yirik tashkilotdir! 🚀\n\n"
            "───────────────\n"
            "📌 <b>Asosiy faktlar:</b>\n"
            "📅 Tashkil etilgan sanasi: 2017-yil 30-iyun\n"
            "🎉 Yoshlar kuni: Har yili 30-iyun mamlakatimizda yoshlar bayrami sifatida nishonlanadi\n"
            "🎯 Asosiy maqsadi: Yoshlarning tashabbuslarini qo‘llab-quvvatlash, ta'lim, tadbirkorlik va kasb-hunar egallashlariga ko‘maklashish\n\n"
            "───────────────\n"
            "🏢 <b>Tashkilot tarkibi:</b>\n"
            "👶 <b>«Kamalak» bolalar tashkiloti</b> — 7 yoshdan 14 yoshgacha bo‘lgan maktab o‘quvchilarini birlashtiradi va ularning iqtidorini rivojlantiradi.\n"
            "🏫 <b>Boshlang‘ich tashkilotlar</b> — Maktablar, kollejlar, litseylar, OTMlar hamda korxona-tashkilotlarda faoliyat yuritadi.\n\n"
            "───────────────\n"
            "🎁 <b>Yoshlar uchun imkoniyatlar va imtiyozlar:</b>\n\n"
            "🎖 <b>Ta'lim va harbiy xizmat:</b>\n"
            "Qurolli Kuchlar safida muddatli harbiy xizmatni o‘tab, Ittifoq tavsiyanomasiga ega bo‘lgan yoshlarga OTMlarga kirishda qo‘shimcha imtiyozli ballar beriladi.\n\n"
            "🎓 <b>Talabalarni qo‘llab-quvvatlash:</b>\n"
            "Faol va a'lochi talabalar uchun shartnoma (kontrakt) to‘lovlarining bir qismini to‘lab berish bo‘yicha moliyaviy yordam ko‘rsatiladi.\n\n"
            "💼 <b>Startap va biznes:</b>\n"
            "Yoshlarning biznes g‘oyalarini amalga oshirish va moliyalashtirish bo‘yicha amaliy ko‘mak beriladi.\n\n"
            "📚 <b>Tanlovlar va loyihalar:</b>\n"
            "«Yosh kitobxon», turli respublika va xalqaro tanlovlar, ilmiy konferensiyalar hamda festivallar muntazam o‘tkaziladi.\n\n"
            "───────────────\n"
            "🌐 <b>Bog‘lanish va rasmiy manbalar:</b>\n"
            "💻 Rasmiy veb-sayt: yoshlar.gov.uz\n"
            "📍 Markaziy kengash: Toshkent shahri."
        ),
        "info_ozdjtu": (
            "🏛 <b>O‘zDJTU Yoshlar Ittifoqi boshlang'ich tashkiloti</b>\n\n"
            "👤 <b>O‘zDJTU Yoshlar ittifoqi yetakchisi:</b>\n"
            "✨ Islomova Sevinch Botirjon qizi\n\n"
            "───────────────\n"
            "🎯 <b>Asosiy faoliyat yo‘nalishlari:</b>\n\n"
            "👥 <b>1. Talaba-yoshlar bilan ishlash</b>\n"
            "Talabalarning ijtimoiy va ma'naviy muhitini yaxshilash, ularni har taraflama qo‘llab-quvvatlash.\n\n"
            "💡 <b>2. Yoshlar tashabbuslarini qo‘llab-quvvatlash</b>\n"
            "Talabalarning yangi g‘oya, loyiha va ijodiy takliflariga yo‘l ochish va amalga oshirishga ko‘maklashish.\n\n"
            "🔄 <b>3. Loyihalarni muvofiqlashtirish</b>\n"
            "Universitet miqyosidagi hamda respublika darajasidagi tadbirlar va tanlovlarni samarali tashkil etish.\n\n"
            "🔍 <b>4. Talabalar muammolarini o‘rganish</b>\n"
            "Yoshlarning murojaat va muammolarini doimiy tahlil qilish hamda ularga yechim topish.\n\n"
            "⚡ <b>5. Yoshlar faolligini oshirish</b>\n"
            "Talabalarning jamoat ishlarida, ilmiy va madaniy tadbirlarda ishtirokini kuchaytirish."
        ),
        "info_coordinators": (
            "👨‍💼 <b>Koordinatorlar va faoliyat yo‘nalishlari</b>\n\n"
            "Universitetimizda yoshlar bilan ishlash jarayonini samarali tashkil etish uchun quyidagi yo‘nalishlar va koordinatorlik tizimi yo‘lga qo‘yilgan:\n\n"
            "🧠 <b>1. Intellektual loyihalar yo‘nalishi</b>\n"
            "Talabalarning mantiqiy fikrlashini va bilim darajasini oshirishga qaratilgan “Zakovat”, munozara klublari va intellektual o‘yinlarni tashkil etadi.\n\n"
            "🎨 <b>2. Besh tashabbus loyihalari yo‘nalishi</b>\n"
            "Madaniyat, san’at, sport, kitobxonlik va axborot texnologiyalarini yoshlar orasida keng targ‘ib qilish va ularning bo‘sh vaqtini mazmunli tashkil etish bilan shug‘ullanadi.\n\n"
            "🎖️ <b>3. Harbiy-vatanparvarlik yo‘nalishi</b>\n"
            "Yoshlarda vatanga sadoqat, milliy g‘urur va harbiy-vatanparvarlik tuyg‘ularini shakllantirishga qaratilgan tadbirlar hamda aksiyalarni o‘tkazadi.\n\n"
            "📢 <b>4. Axborot va media yo‘nalishi</b>\n"
            "Universitet hayotidagi yangiliklarni keng yoritish, SMM, fotoreportajlar, video roliklar tayyorlash va ijtimoiy tarmoqlardagi sahifalarni yuritishni muvofiqlashtiradi.\n\n"
            "💡 <b>5. Tadbirkorlik va innovatsion loyihalar yo‘nalishi</b>\n"
            "Talabalarning biznes g‘oyalarini, startap loyihalarini qo‘llab-quvvatlaydi hamda innovatsion ishlanmalarini amaliyotga tatbiq etishda ko‘maklashadi.\n\n"
            "👧 <b>6. Talaba qizlar yo‘nalishi</b>\n"
            "Talaba qizlarning jamiyatdagi o‘rnini oshirish, ularning iqtidorini yuzaga chiqarish hamda tazyiq va zo‘ravonlikdan xoli muhit yaratish bo‘yicha ish olib boradi.\n\n"
            "📋 <b>7. “Yoshlar daftari” va mecenatlik yo‘nalishi</b>\n"
            "Ijtimoiy himoyaga muhtoj talabalarni aniqlash, ularga moddiy va ma’naviy yordam ko‘rsatish hamda homiylik loyihalarini muvofiqlashtiradi.\n\n"
            "💻 <b>8. IT va dasturlash yo‘nalishi</b>\n"
            "Dasturlash, zamonaviy texnologiyalar, dizayn va IT sohasiga qiziquvchi yoshlarni birlashtiradi hamda tegishli o‘quv kurslari va xakatolarni tashkil etadi.\n\n"
            "🌱 <b>9. Eko-taraqqiyot va “yashil g‘oyalar” yo‘nalishi</b>\n"
            "Atrof-muhitni muhofaza qilish, ecologik madaniyatni oshirish va “Yashil makon” loyihalari doirasida obodonlashtirish aksiyalarini o‘tkazadi.\n\n"
            "🏡 <b>10. Talabalar turar joyi (TTJ) yo‘nalishi</b>\n"
            "Yotoqxonada istiqomat qiluvchi talabalar uchun qulay yashash sharoitlarini nazorat qiladi va ularning bo‘sh vaqtini mazmunli o‘tkazish bo‘yicha tadbirlar uyushtiradi.\n\n"
            "🎭 <b>11. San’at va madaniyat yo‘nalishi</b>\n"
            "Musiqa, raqs, teatr va tasviriy san’atga qiziquvchi iqtidorli talabalarni kashf etadi hamda konsert va ko‘rik-tanlovlarni tashkil qiladi."
        ),
        "students_info": (
            "📚 <b>Talabalar uchun bo'limi:</b>\n\nUshbu bo'lim tez orada to'liq"
            " ishga tushiriladi va foydali ma'lumotlar bilan to'ldiriladi! ⏳"
        ),
        "send_proposal_prompt": (
            "💡 Iltimos, o'z taklif, g'oya yoki murojaatingizni batafsil matn"
            " shaklida yuboring:"
        ),
        "proposal_success": (
            "✅ Rahmat! Sizning taklifingiz muvaffaqiyatli qabul qilindi va"
            " mas'ullarga yuborildi."
        ),
        "no_news": "📰 Hozircha hech qanday yangilik joylanmagan.",
    },
    "ru": {
        "welcome": "Добро пожаловать! Выберите нужный раздел:",
        "menu_1": "ℹ️ О Союзе молодежи",
        "menu_2": "🏛 Союз молодежи УзГУМЯ",
        "menu_3": "👥 О координаторах",
        "menu_4": "📰 Новости и объявления",
        "menu_5": "📚 Для студентов",
        "menu_6": "💡 Отправить предложение",
        "change_lang": "🌐 Сменить язык",
        "back": "⬅️ Назад",
        "info_yi": (
            "🌟 <b>О Союзе молодежи Узбекистана</b>\n\nСоюз молодежи Узбекистана"
            " — крупная организация, всесторонне поддерживающая молодежь"
            " нашей страны! 🚀\n\n───────────────\n📌 <b>Основные факты:</b>\n📅"
            " Дата основания: 30 июня 2017 г.\n🎉 День молодежи: 30 июня\n\n🌐"
            " Официальный сайт: yoshlar.gov.uz"
        ),
        "info_ozdjtu": (
            "🏛 <b>Первичная организация Союза молодежи УзГУМЯ</b>\n\n👤"
            " <b>Лидер Союза молодежи УзГУМЯ:</b>\n✨ Исломова Севинч Ботиржон"
            " кизи\n\n───────────────\n🎯 <b>Основные направления"
            " деятельности:</b>\n👥 1. Работа со студентами\n💡 2. Поддержка"
            " инициатив молодежи\n🔄 3. Координация проектов\n🔍 4. Изучение"
            " проблем студентов\n⚡ 5. Повышение активности молодежи"
        ),
        "info_coordinators": (
            "👨‍💼 <b>Координаторы и направления деятельности</b>\n\n1."
            " Интеллектуальные проекты\n2. Пять инициатив\n3."
            " Военно-патриотическое направление\n4. Медиа и SMM\n5. IT и"
            " программирование"
        ),
        "students_info": (
            "📚 <b>Раздел для студентов:</b>\n\nЭтот раздел скоро будет запущен"
            " и заполнен полезной информацией! ⏳"
        ),
        "send_proposal_prompt": "💡 Отправьте ваше предложение:",
        "proposal_success": "✅ Ваше предложение принято!",
        "no_news": "📰 Пока нет опубликованных новостей.",
    },
    "en": {
        "welcome": "Welcome! Select a section:",
        "menu_1": "ℹ About Youth Union",
        "menu_2": "🏛 UzSWLU Youth Union",
        "menu_3": "👥 About Coordinators",
        "menu_4": "📰 News and Announcements",
        "menu_5": "📚 For Students",
        "menu_6": "💡 Send Proposal",
        "change_lang": "🌐 Change Language",
        "back": "⬅️ Back",
        "info_yi": (
            "🌟 <b>About Youth Union of Uzbekistan</b>\n\nYouth Union of"
            " Uzbekistan is a major organization that fully supports the"
            " youth of our country! 🚀\n\n───────────────\n📌 <b>Key"
            " Facts:</b>\n📅 Founded: June 30, 2017\n🎉 Youth Day: June"
            " 30\n\n🌐 Official Website: yoshlar.gov.uz"
        ),
        "info_ozdjtu": (
            "🏛 <b>UzSWLU Youth Union Primary Organization</b>\n\n👤 <b>Leader of"
            " UzSWLU Youth Union:</b>\n✨ Islomova Sevinch Botirjon"
            " qizi\n\n───────────────\n🎯 <b>Main Areas of Activity:</b>\n👥 1."
            " Working with students\n💡 2. Supporting youth initiatives\n🔄 3."
            " Project coordination\n🔍 4. Addressing student issues\n⚡ 5."
            " Boosting student engagement"
        ),
        "info_coordinators": (
            "👨‍💼 <b>Coordinators and Areas:</b>\n\n1. Intellectual Projects\n2."
            " 5 Initiatives\n3. Media & SMM\n4. IT & Programming"
        ),
        "students_info": (
            "📚 <b>For Students section:</b>\n\nThis section will be available"
            " and updated soon! ⏳"
        ),
        "send_proposal_prompt": "💡 Please send your proposal:",
        "proposal_success": "✅ Your proposal has been received!",
        "no_news": "📰 No news posted yet.",
    },
}


def language_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_uz = types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    markup.add(btn_uz, btn_ru, btn_en)
    return markup


def main_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    t = TEXTS.get(lang, TEXTS["uz"])
    markup.add(types.KeyboardButton(t["menu_1"]), types.KeyboardButton(t["menu_2"]))
    markup.add(types.KeyboardButton(t["menu_3"]), types.KeyboardButton(t["menu_4"]))
    markup.add(types.KeyboardButton(t["menu_5"]), types.KeyboardButton(t["menu_6"]))
    markup.add(types.KeyboardButton(t["change_lang"]))
    return markup


def back_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    t = TEXTS.get(lang, TEXTS["uz"])
    markup.add(types.KeyboardButton(t["back"]))
    return markup


# ----------------- ADMIN BUYRUQLARI -----------------
@bot.message_handler(commands=["stats"])
def admin_stats(message):
    if message.from_user.id == ADMIN_ID:
        total = get_stats()
        bot.send_message(
            message.chat.id,
            f"📊 <b>Bot foydalanuvchilari statistikasi:</b>\n\nJami"
            f" foydalanuvchilar soni: <b>{total} ta</b>",
            parse_mode="HTML",
        )
    else:
        bot.send_message(message.chat.id, "Siz admin emassiz!")


@bot.message_handler(commands=["send"])
def admin_broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(
            message.chat.id,
            "📢 Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting:",
        )
        bot.register_next_step_handler(msg, process_broadcast)
    else:
        bot.send_message(message.chat.id, "Siz admin emassiz!")


def process_broadcast(message):
    users = get_all_users()
    success = 0
    failed = 0
    bot.send_message(ADMIN_ID, "🚀 Xabar yuborish boshlandi...")

    for user_id in users:
        try:
            bot.send_message(user_id, message.text)
            success += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.send_message(
        ADMIN_ID,
        f"✅ <b>Xabar yuborildi!</b>\n\nMuvaffaqiyatli:"
        f" {success} ta\nMuvaffaqiyatsiz: {failed} ta",
        parse_mode="HTML",
    )


@bot.message_handler(commands=["addnews"])
def admin_add_news(message):
    """Admin yangilik postini joylashi uchun"""
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(
            message.chat.id,
            "📸 Yangilik uchun **rasm** yuboring (rasm ostiga matnini ham"
            " yozishingiz mumkin):",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(msg, process_add_news)
    else:
        bot.send_message(message.chat.id, "Siz admin emassiz!")


def process_add_news(message):
    if message.photo:
        photo_id = message.photo[-1].file_id
        caption = message.caption if message.caption else "Yangilik"
        add_news(photo_id, caption)
        bot.send_message(
            ADMIN_ID,
            "✅ Yangilik muvaffaqiyatli saqlandi va foydalanuvchilarga ko'rinadi!",
        )
    else:
        bot.send_message(
            ADMIN_ID, "⚠️ Iltimos, yangilik uchun rasm va izoh yuboring."
        )


# ----------------- ASOSIY HANDLERLAR -----------------
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user = message.from_user
    add_user(user.id, user.first_name, user.username)

    bot.send_message(
        message.chat.id,
        "Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please select"
        " a language:",
        reply_markup=language_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_language(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.message.chat.id, lang)

    # Xabar topilmasa xatolik bermasligi uchun try-except qo'shildi
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    t = TEXTS[lang]
    bot.send_message(
        call.message.chat.id, t["welcome"], reply_markup=main_menu(lang)
    )


def process_proposal(message):
    chat_id = message.chat.id
    lang = get_user_lang(chat_id)
    t = TEXTS[lang]

    if message.text in ["⬅ Ortga", "⬅️ Ortga", "⬅ Назад", "⬅ Back"]:
        bot.send_message(chat_id, t["welcome"], reply_markup=main_menu(lang))
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "Mavjud emas"
    first_name = (
        html.escape(user.first_name) if user.first_name else "Foydalanuvchi"
    )
    user_text = html.escape(message.text) if message.text else ""

    admin_message = (
        "📥 <b>Yangi taklif/murojaat kelib tushdi!</b>\n\n"
        f"👤 <b>Yuboruvchi:</b> {first_name}\n"
        f"🌐 <b>Username:</b> {username}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n\n"
        f"💬 <b>Murojaat matni:</b>\n{user_text}"
    )

    try:
        bot.send_message(ADMIN_ID, admin_message, parse_mode="HTML")
        bot.send_message(
            chat_id, t["proposal_success"], reply_markup=main_menu(lang)
        )
    except Exception as e:
        print(f"Xatolik: {e}")
        bot.send_message(
            chat_id, "⚠️ Xatolik yuz berdi.", reply_markup=main_menu(lang)
        )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    user = message.from_user
    add_user(user.id, user.first_name, user.username)

    lang = get_user_lang(chat_id)
    t = TEXTS[lang]
    text = message.text

    if text in [
        "🌐 Tilni o'zgartirish",
        "🌐 Сменить язык",
        "🌐 Change Language",
    ]:
        bot.send_message(
            chat_id,
            "Tilni tanlang / Выберите язык / Select language:",
            reply_markup=language_keyboard(),
        )
        return

    if text in ["⬅️ Ortga", "⬅ Ortga", "⬅ Назад", "⬅ Back"]:
        bot.send_message(chat_id, t["welcome"], reply_markup=main_menu(lang))
        return

    # Asosiy bo'limlar
    if text in [
        TEXTS["uz"]["menu_1"],
        TEXTS["ru"]["menu_1"],
        TEXTS["en"]["menu_1"],
    ]:
        bot.send_message(
            chat_id,
            t["info_yi"],
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=back_menu(lang),
        )

    elif text in [
        TEXTS["uz"]["menu_2"],
        TEXTS["ru"]["menu_2"],
        TEXTS["en"]["menu_2"],
    ]:
        bot.send_message(
            chat_id,
            t["info_ozdjtu"],
            parse_mode="HTML",
            reply_markup=back_menu(lang),
        )

    elif text in [
        TEXTS["uz"]["menu_3"],
        TEXTS["ru"]["menu_3"],
        TEXTS["en"]["menu_3"],
    ]:
        bot.send_message(
            chat_id,
            t["info_coordinators"],
            parse_mode="HTML",
            reply_markup=back_menu(lang),
        )

    # Yangiliklar bo'limi
    elif text in [
        TEXTS["uz"]["menu_4"],
        TEXTS["ru"]["menu_4"],
        TEXTS["en"]["menu_4"],
    ]:
        news = get_latest_news()
        if news:
            for item in news:
                photo_id, caption, created_at = item
                bot.send_photo(
                    chat_id, photo_id, caption=f"{caption}\n\n📅 {created_at}"
                )
        else:
            bot.send_message(
                chat_id, t["no_news"], reply_markup=back_menu(lang)
            )

    # Talabalar uchun bo'limi
    elif text in [
        TEXTS["uz"]["menu_5"],
        TEXTS["ru"]["menu_5"],
        TEXTS["en"]["menu_5"],
    ]:
        bot.send_message(
            chat_id,
            t["students_info"],
            parse_mode="HTML",
            reply_markup=back_menu(lang),
        )

    # Taklif yuborish
    elif text in [
        TEXTS["uz"]["menu_6"],
        TEXTS["ru"]["menu_6"],
        TEXTS["en"]["menu_6"],
    ]:
        msg = bot.send_message(
            chat_id, t["send_proposal_prompt"], reply_markup=back_menu(lang)
        )
        bot.register_next_step_handler(msg, process_proposal)

    else:
        bot.send_message(chat_id, t["welcome"], reply_markup=main_menu(lang))


if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)