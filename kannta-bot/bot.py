import json
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.client.default import DefaultBotProperties

# === Конфигурация ===
API_TOKEN = '7731287979:AAEEeOHdo1tIIa_b0oIb9qNwoQ9ZjJsz1Cc'  # Замените на токен вашего бота
GROUP_CHAT_ID = -1002841459949  # ID вашей группы (бот должен быть в группе)
WEB_APP_URL = 'https://doswstds.github.io/kataanse/'  # Замените на ссылку на ваше веб-приложение

# === Инициализация бота и диспетчера ===
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

USERS_FILE = "use12121rs.json"

# === Работа с файлом пользователей ===
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# === Хэндлер для /start ===
@dp.message(CommandStart())
async def start(message: types.Message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id in users:
        # Пользователь уже подтверждён — даём кнопку на веб-апп
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в веб-приложение", web_app=WebAppInfo(url=WEB_APP_URL))]
        ])
        await message.answer("👋 Добро пожаловать обратно!", reply_markup=keyboard)
    else:
        # Кнопка подтверждения номера телефона
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📞 Подтвердить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Пожалуйста, подтвердите свой номер телефона:", reply_markup=kb)

# === Обработка номера телефона ===
@dp.message(F.contact)
async def handle_contact(message: types.Message):
    contact = message.contact
    user_id = str(message.from_user.id)

    users = load_users()
    users[user_id] = {
        "phone_number": contact.phone_number,
        "username": message.from_user.username
    }
    save_users(users)

    # Удалить клавиатуру
    await message.answer("✅ Номер телефона успешно подтверждён!", reply_markup=ReplyKeyboardRemove())

    # Уведомление в чат
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"📱 Новый пользователь подтвердил номер телефона: @{message.from_user.username or 'Без имени'}"
        )
    except Exception as e:
        logging.warning(f"Ошибка отправки сообщения в группу: {e}")

    # Кнопка веб-аппа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в веб-приложение", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer("Нажмите кнопку ниже, чтобы перейти в веб-приложение:", reply_markup=keyboard)

# === Точка входа ===
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
