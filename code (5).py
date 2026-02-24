
# main.py
import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, F, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ (рекомендовано через переменные окружения) ---
BOT_TOKEN = os.getenv("8732983685:AAEZbabNClZ5C4lRQMXKhiMbGMxg8ZmO4_c")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # если будете использовать replicate

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не найден в переменных окружения. Установите BOT_TOKEN и перезапустите.")
    raise SystemExit(1)

# Если нужно, можно установить os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для ИИ
class AIState(StatesGroup):
    wait_prompt = State()

# --- КЛАВИАТУРЫ (СТИЛЬ ZELDRIS) ---
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Магазин услуг", callback_data="shop")],
        [InlineKeyboardButton(text="🎬 ИИ Видео-генератор", callback_data="ai_video")],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="🤝 Рефералы", callback_data="refs")
        ],
        [
            InlineKeyboardButton(text="⭐️ Отзывы", url="https://t.me/zeldris_shp"),
            InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/zeldris_weelfare")
        ]
    ])

def shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Купить Звёзды (Stars)", callback_data="buy_stars")],
        [InlineKeyboardButton(text="💎 Telegram Premium", callback_data="buy_premium")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
    ])

def stars_prices_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 ⭐️ — 150₽", callback_data="pay_stars_50")],
        [InlineKeyboardButton(text="100 ⭐️ — 290₽", callback_data="pay_stars_100")],
        [InlineKeyboardButton(text="500 ⭐️ — 1350₽", callback_data="pay_stars_500")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="shop")]
    ])

# Вспомогательная функция для показа главного меню (чтобы не дублировать код)
async def send_main_menu(message: Message):
    welcome_text = (
        f"👋 *Привет, {message.from_user.first_name}!* \n\n"
        f"Добро пожаловать в *Zeldris Hub* — твой личный сервис по прокачке Telegram!\n\n"
        f"🔹 Сервис по покупкам и подпискам\n"
        f"🔹 ИИ видео и генерация по тексту\n\n"
        f"Выбирай нужный раздел ниже: 👇"
    )
    await message.answer(welcome_text, reply_markup=main_menu_kb(), parse_mode=types.ParseMode.MARKDOWN)

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start_handler(message: Message):
    await send_main_menu(message)

@dp.callback_query(F.data == "to_main")
async def to_main(call: CallbackQuery):
    # просто отправляем главное меню — используем call.message.reply, а не вызов handler'а напрямую
    if call.message:
        await call.message.edit_text("Возвращаемся в главное меню:", reply_markup=main_menu_kb())

# Раздел Магазин
@dp.callback_query(F.data == "shop")
async def shop_menu(call: CallbackQuery):
    if call.message:
        await call.message.edit_text("🛍 *Магазин Zeldris*\n\nВыбери категорию товара:", 
                                     reply_markup=shop_kb(), parse_mode=types.ParseMode.MARKDOWN)

@dp.callback_query(F.data == "buy_stars")
async def stars_menu(call: CallbackQuery):
    if call.message:
        await call.message.edit_text("⭐️ *Покупка Звёзд (Telegram Stars)*\n\nВыберите количество:", 
                                     reply_markup=stars_prices_kb(), parse_mode=types.ParseMode.MARKDOWN)

# Раздел Профиль
@dp.callback_query(F.data == "profile")
async def profile_menu(call: CallbackQuery):
    if not call.message:
        return
    profile_text = (
        f"👤 *Ваш профиль Zeldris*\n\n"
        f"ID: `{call.from_user.id}`\n"
        f"Баланс: `0 ⭐️`\n"
        f"Покупок: `0`\n\n"
        f"За приглашение друзей вы получаете бонусы!"
    )
    await call.message.edit_text(profile_text, 
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="➕ Пополнить баланс", callback_data="shop")],
                                     [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
                                 ]), parse_mode=types.ParseMode.MARKDOWN)

# Реферальная система
@dp.callback_query(F.data == "refs")
async def refs_menu(call: CallbackQuery):
    if not call.message:
        return
    me = await bot.get_me()
    bot_username = me.username or "your_bot"
    ref_link = f"https://t.me/{bot_username}?start={call.from_user.id}"
    ref_text = (
        f"🤝 *Реферальная программа*\n\n"
        f"Приглашайте друзей и получайте 5% от их покупок на ваш баланс!\n\n"
        f"🔗 Ваша ссылка:\n`{ref_link}`"
    )
    await call.message.edit_text(ref_text, 
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
                                 ]), parse_mode=types.ParseMode.MARKDOWN)

# --- ЛОГИКА ИИ (ВИДЕО) ---
@dp.callback_query(F.data == "ai_video")
async def ai_start(call: CallbackQuery, state: FSMContext):
    if not call.message:
        return
    await call.message.edit_text(
        "🎬 *Генератор Видео*\n\nНапиши, что должно быть на видео (на английском):\n_Пример: A cat playing piano_", 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="to_main")]
        ]), parse_mode=types.ParseMode.MARKDOWN
    )
    await state.set_state(AIState.wait_prompt)

@dp.message(StateFilter(AIState.wait_prompt))
async def ai_process(message: Message, state: FSMContext):
    prompt = message.text or ""
    await state.clear()
    
    status_msg = await message.answer("⏳ *Zeldris AI начал генерацию...* \nОбычно это занимает 1-2 минуты.", parse_mode=types.ParseMode.MARKDOWN)
    
    try:
        import replicate
        # Пример вызова модели — это демонстрация; реальная модель/входы могут отличаться.
        # Здесь мы просто показываем шаблон — проверьте документацию replicate для нужной модели.
        output = replicate.run(
            "stability-ai/stable-video-diffusion:3f045714",
            input={"prompt": prompt}
        )
        # output может быть URL или список — отобразим в сообщении ссылку или отправим как видео, если это файл.
        if isinstance(output, (list, tuple)) and output:
            video_url = output[0]
        else:
            video_url = output
        await bot.send_message(message.chat.id, f"✨ Видео по запросу: {prompt}\n{video_url}")
        await status_msg.delete()
    except Exception as e:
        logging.exception("Error generating video")
        await status_msg.edit_text("❌ Ошибка генерации. Проверьте баланс Replicate или корректность запроса.")

# --- Запуск ---
async def main():
    logging.info("Бот Zeldris запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот выключен")
