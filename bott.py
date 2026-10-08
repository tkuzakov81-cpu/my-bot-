import json
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import random


# ============================================================
# НАСТРОЙКИ
# ============================================================

BOT_TOKEN = "8434371618:AAF3nMtjswYHXF-xpDnzq7SynT2IcXiDgP4"

# Файл, в котором будут храниться профили пользователей
USER_FILE = "user.json"


# ============================================================
# ЗАГРУЗКА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

def load_users():
    # Если файла ещё нет — создаём пустой словарь
    if not os.path.exists(USER_FILE):
        return {}

    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        # Если файл повреждён или не читается
        return {}


# Загружаем пользователей при запуске программы
user_data = load_users()


# ============================================================
# СОХРАНЕНИЕ ДАННЫХ
# ============================================================

def save_users():
    # Сохраняем словарь пользователей в JSON-файл
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(
            user_data,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================

def main_menu():

    keyboard = [
        [
            "📚 Факт о литературе",
            "💬 Случайная цитата"
        ],
        [
            "📖 Совет по книге",
            "🎲 Случайный факт"
        ],
        [
            "👤 Мой профиль",
            "ℹ️ Помощь"
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


# ============================================================
# ДАННЫЕ ЛИТЕРАТУРЫ
# ============================================================

literature_facts = [
    "📚 Лев Толстой работал над романом «Война и мир» около 6 лет.",
    "📚 «Дон Кихот» Мигеля де Сервантеса считается одним из первых современных европейских романов.",
    "📚 Уильям Шекспир написал около 39 пьес.",
    "📚 «Преступление и наказание» Фёдора Достоевского впервые было опубликовано в 1866 году.",
    "📚 Александр Пушкин написал «Евгения Онегина» в стихах.",
    "📚 Гомер традиционно считается автором «Илиады» и «Одиссеи»."
]


quotes = [
    "💬 «Красота спасёт мир». — Фёдор Достоевский",
    "💬 «Мы в ответе за тех, кого приручили». — Антуан де Сент-Экзюпери",
    "💬 «Человек — это звучит гордо!» — Максим Горький",
    "💬 «А счастье было так возможно, так близко!» — Александр Пушкин"
]


book_advice = [
    "📖 Попробуй прочитать «Преступление и наказание» Ф. М. Достоевского.",
    "📖 Если нравится антиутопия — попробуй «1984» Джорджа Оруэлла.",
    "📖 Для знакомства с русской классикой можно начать с рассказов Антона Чехова.",
    "📖 Если интересна философская литература — попробуй «Мастера и Маргариту» Михаила Булгакова.",
    "📖 Если хочется приключений — попробуй «Графа Монте-Кристо» Александра Дюма."
]


random_facts = [
    "🎲 Шекспир и Сервантес умерли 23 апреля 1616 года.",
    "🎲 Александрийская библиотека была одним из крупнейших интеллектуальных центров античного мира.",
    "🎲 Первые известные письменные произведения человечества появились несколько тысяч лет назад.",
    "🎲 Слово «литература» происходит от латинского litteratura."
]


# ============================================================
# ПРОВЕРКА ПРОФИЛЯ
# ============================================================

def get_user(user_id):

    # user_id превращаем в строку,
    # потому что JSON хранит ключи словаря как строки
    user_id = str(user_id)

    return user_data.get(user_id)


# ============================================================
# КОМАНДА /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    # Если пользователь уже зарегистрирован
    if user_id in user_data:

        name = user_data[user_id]["name"]

        await update.message.reply_text(
            f"👋 С возвращением, {name}!\n\n"
            "Выбери нужную функцию в меню 👇",
            reply_markup=main_menu()
        )

        return

    # Создаём новый профиль
    user_data[user_id] = {
        "name": "",
        "color": ""
    }

    # Сохраняем профиль
    save_users()

    # Запоминаем, что сейчас нужно получить имя
    context.user_data["registration_step"] = "name"

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Давай создадим твой профиль.\n\n"
        "Как тебя зовут?"
    )


# ============================================================
# РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# ============================================================

async def registration_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Проверяем, находится ли пользователь
    # сейчас на этапе регистрации
    step = context.user_data.get("registration_step")

    if not step:
        return False

    user_id = str(update.effective_user.id)

    # Проверяем существование профиля
    if user_id not in user_data:
        user_data[user_id] = {
            "name": "",
            "color": ""
        }

    text = update.message.text.strip()

    # --------------------------------------------------------
    # ЭТАП 1 — ИМЯ
    # --------------------------------------------------------

    if step == "name":

        if not text:
            await update.message.reply_text(
                "❌ Имя не может быть пустым.\n"
                "Попробуй ещё раз:"
            )
            return True

        # Сохраняем имя
        user_data[user_id]["name"] = text

        save_users()

        # Переходим к выбору цвета
        context.user_data["registration_step"] = "color"

        color_keyboard = [
            ["🔴 Красный", "🔵 Синий"],
            ["🟢 Зелёный", "🟡 Жёлтый"],
            ["🟣 Фиолетовый", "⚫ Чёрный"]
        ]

        await update.message.reply_text(
            f"Отлично, {text}! 👍\n\n"
            "Теперь выбери свой любимый цвет:",
            reply_markup=ReplyKeyboardMarkup(
                color_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

        return True

    # --------------------------------------------------------
    # ЭТАП 2 — ЦВЕТ
    # --------------------------------------------------------

    if step == "color":

        # Убираем эмодзи из названия цвета
        color = text

        colors = {
            "🔴 Красный": "Красный",
            "🔵 Синий": "Синий",
            "🟢 Зелёный": "Зелёный",
            "🟡 Жёлтый": "Жёлтый",
            "🟣 Фиолетовый": "Фиолетовый",
            "⚫ Чёрный": "Чёрный"
        }

        if text in colors:
            color = colors[text]

        else:
            await update.message.reply_text(
                "❌ Пожалуйста, выбери цвет с помощью кнопок."
            )
            return True

        # Сохраняем цвет
        user_data[user_id]["color"] = color

        # Сохраняем изменения в JSON
        save_users()

        # Регистрация закончена
        context.user_data.pop("registration_step", None)

        name = user_data[user_id]["name"]

        await update.message.reply_text(
            "✅ Профиль успешно создан!\n\n"
            f"👤 Имя: {name}\n"
            f"🎨 Цвет: {color}\n\n"
            "Теперь тебе доступны все функции бота 👇",
            reply_markup=main_menu()
        )

        return True

    return False


# ============================================================
# КОМАНДА /PROFILE
# ============================================================

async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = str(update.effective_user.id)

    # Получаем профиль пользователя
    user = get_user(user_id)

    # Если профиля нет
    if not user or not user.get("name"):

        await update.message.reply_text(
            "❌ У тебя пока нет профиля.\n\n"
            "Используй /start для его создания.",
            reply_markup=main_menu()
        )

        return

    await update.message.reply_text(
        "👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"📝 Имя: {user['name']}\n"
        f"🎨 Любимый цвет: {user['color']}\n\n"
        f"🆔 ID: {user_id}",
        reply_markup=main_menu()
    )


# ============================================================
# ПОМОЩЬ
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ ПОМОЩЬ\n\n"

        "📚 Факт о литературе — случайный факт.\n\n"

        "💬 Случайная цитата — случайная цитата.\n\n"

        "📖 Совет по книге — рекомендация книги.\n\n"

        "🎲 Случайный факт — интересный факт.\n\n"

        "👤 Мой профиль — показать сохранённые данные.\n\n"

        "/start — запустить бота\n"
        "/profile — показать профиль\n"
        "/help — показать помощь",

        reply_markup=main_menu()
    )


# ============================================================
# ОБРАБОТКА КНОПОК
# ============================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    # Факт о литературе
    if text == "📚 Факт о литературе":

        await update.message.reply_text(
            random.choice(literature_facts),
            reply_markup=main_menu()
        )

    # Случайная цитата
    elif text == "💬 Случайная цитата":

        await update.message.reply_text(
            random.choice(quotes),
            reply_markup=main_menu()
        )

    # Совет по книге
    elif text == "📖 Совет по книге":

        await update.message.reply_text(
            random.choice(book_advice),
            reply_markup=main_menu()
        )

    # Случайный факт
    elif text == "🎲 Случайный факт":

        await update.message.reply_text(
            random.choice(random_facts),
            reply_markup=main_menu()
        )

    # Профиль
    elif text == "👤 Мой профиль":

        await profile(update, context)

    # Помощь
    elif text == "ℹ️ Помощь":

        await help_command(update, context)


# ============================================================
# ОБЩИЙ ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Сначала проверяем, проходит ли пользователь регистрацию
    registration = await registration_handler(
        update,
        context
    )

    # Если это была регистрация —
    # дальше сообщение не обрабатываем
    if registration:
        return

    # Иначе обрабатываем обычные кнопки
    await button_handler(update, context)


# ============================================================
# ЗАПУСК БОТА
# ============================================================

def main():

    # Создаём приложение Telegram-бота
    app = Application.builder().token(BOT_TOKEN).build()

    # Команда /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # Команда /help
    app.add_handler(
        CommandHandler("help", help_command)
    )

    # Команда /profile
    app.add_handler(
        CommandHandler("profile", profile)
    )

    # Обработка обычных текстовых сообщений и кнопок
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("🤖 Бот запущен!")

    # Запускаем постоянное получение сообщений
    app.run_polling()


# ============================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================

if __name__ == "__main__":
    main()
    # 1. Переменные с твоими данными
my_name = "Arman"
my_age = 15
my_hobby = "бэкенд-разработка"

# 2. Функция /about — заполни f-string своими фактами
async def about(update, context):
    text = (
        f"Привет! Меня зовут {my_name}.\n"
        f"Мне {my_age} лет.\n"
        f"Моё хобби: {my_hobby}.\n"
        "Меня создал ученик CAP Education 😎"
    )
    await update.message.reply_text(text)

# 3. ВАЖНО: не забудь зарегистрировать хендлер!
class app:
    ...

app.add_handler(CommandHandler("about", about))

# Подсказка: где взять данные в тренажёре?
# Питонтьютор → раздел «Переменные и типы» (слева в меню)
# Снейк.про → snakify.org → тема Integer and float numbers
