from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import executor
import currencyAPI

# Токен API Telegram-бота
API_TOKEN = ''

# Создание объекта бота
bot = Bot(token=API_TOKEN)

# Создание диспетчера для обработки сообщений
dp = Dispatcher(bot)

# Настройка логгирования для отладки
dp.middleware.setup(LoggingMiddleware())

# Создание клавиатуры с валютными парами
keyboard = types.InlineKeyboardMarkup()
keyboard.add(
    types.InlineKeyboardButton(text="EUR/RUB", callback_data="EUR_RUB"),
    types.InlineKeyboardButton(text="TRY/RUB", callback_data="TRY_RUB"),
    types.InlineKeyboardButton(text="RSD/RUB", callback_data="RSD_RUB"),
    types.InlineKeyboardButton(text="GBP/RUB", callback_data="GBP_RUB"),
    types.InlineKeyboardButton(text="USD/RUB", callback_data="USD_RUB"),
    types.InlineKeyboardButton(text="MXB/RUB", callback_data="MXB_RUB"),
    types.InlineKeyboardButton(text="JPY/RUB", callback_data="JPY_RUB"),
    types.InlineKeyboardButton(text="CNY/RUB", callback_data="CNY_RUB"),
    types.InlineKeyboardButton(text="IRR/RUB", callback_data="IRR_RUB"))

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Отправка приветственного сообщения с клавиатурой
    await message.answer("Выберите валютную пару:", reply_markup=keyboard)

# Обработчик нажатия на кнопки клавиатуры
@dp.callback_query_handler(lambda query: query.data in [
    "EUR_RUB", "TRY_RUB", "RSD_RUB", "GBP_RUB", "USD_RUB", "MXB_RUB",
    "JPY_RUB", "CNY_RUB", "IRR_RUB"
])
async def process_callback(callback_query: types.CallbackQuery):
    # Удаление предыдущего сообщения с клавиатурой
    await bot.delete_message(callback_query.message.chat.id,
                             callback_query.message.message_id)
    # Подтверждение получения запроса
    await bot.answer_callback_query(callback_query.id)

    # Получение валютной пары из данных запроса
    currency_pair = callback_query.data

    # Извлечение целевой валюты из валютной пары
    target_currency = currency_pair.split("_")[0]

    # Получение курса из API currencyAPI.py
    exchange_rate = currencyAPI.convert_currency(1, target_currency)

    # Проверка на наличие ошибки в API
    if isinstance(exchange_rate, str):  
        # Вывод ошибки
        await bot.send_message(callback_query.from_user.id,
                               exchange_rate) 
    else:
        # Формирование сообщения с курсом
        await bot.send_message(
            callback_query.from_user.id,
            f"Актуальный курс {target_currency}/RUB: {exchange_rate}")

    # Создание клавиатуры с кнопкой "Назад"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="back"))
    # Отправка сообщения с клавиатурой
    await bot.send_message(callback_query.from_user.id,
                           "Выберите валютную пару:",
                           reply_markup=keyboard)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
