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
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇪🇺 EUR", callback_data="EUR_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇹🇷 TRY", callback_data="TRY_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇷🇸 RSD", callback_data="RSD_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇬🇧 GBP", callback_data="GBP_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇺🇸 USD", callback_data="USD_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇲🇽 MXB", callback_data="MXB_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇯🇵 JPY", callback_data="JPY_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇨🇳 CNY", callback_data="CNY_RUB"),
    types.InlineKeyboardButton(text="🇷🇺 RUB/🇮🇷 IRR", callback_data="IRR_RUB"))

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Отправка приветственного сообщения с клавиатурой
    await message.answer("Привет! Хотите узнать курс валюты? 😉", reply_markup=keyboard)

# Обработчик нажатия на кнопки клавиатуры
@dp.callback_query_handler(lambda query: query.data in [
    "EUR_RUB", "TRY_RUB", "RSD_RUB", "GBP_RUB", "USD_RUB", "MXB_RUB",
    "JPY_RUB", "CNY_RUB", "AED_RUB"
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

    # Создание клавиатуры с кнопкой "Назад"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад",
                                            callback_data="back"))

    # Проверка на наличие ошибки в API
    if isinstance(exchange_rate, str):  
        # Вывод ошибки
        await bot.send_message(callback_query.from_user.id,
                               exchange_rate) 
    else:
        # Сохранение целевой валюты для калькулятора
        global target_currency_for_calc
        target_currency_for_calc = target_currency

        # Формирование сообщения с курсом
        await bot.send_message(
            callback_query.from_user.id,
            f"Актуальный курс {target_currency}/RUB: {exchange_rate}\n\nНапишите сумму в рублях, а бот вам отправит сумму в {target_currency}",
            reply_markup=keyboard) 

# Обработчик кнопки "Назад"
@dp.callback_query_handler(lambda query: query.data == "back")
async def process_back_callback(callback_query: types.CallbackQuery):
    # Удаление предыдущего сообщения с курсом
    await bot.delete_message(callback_query.message.chat.id,
                             callback_query.message.message_id)
    # Подтверждение получения запроса
    await bot.answer_callback_query(callback_query.id)
    # Отправка стартового сообщения с клавиатурой
    await bot.send_message(callback_query.from_user.id,
                           "Привет! Хотите узнать курс валюты? 😉",
                           reply_markup=keyboard) 

# Обработчик текстового сообщения после выбора валюты
@dp.message_handler(lambda message: message.text.isdigit())
async def process_amount(message: types.Message):
    # Получение суммы из сообщения
    amount = int(message.text)

    # Получение курса из API currencyAPI.py
    exchange_rate = currencyAPI.convert_currency(1, target_currency_for_calc)

    # Проверка на наличие ошибки в API
    if isinstance(exchange_rate, str):  
        # Вывод ошибки
        await bot.send_message(message.from_user.id,
                               exchange_rate) 
    else:
        # Вычисление конвертированной суммы
        converted_amount = amount / exchange_rate

        # Формирование сообщения с конвертированной суммой
        await bot.send_message(message.from_user.id,
                               f"{amount} рублей = {converted_amount:.2f} {target_currency_for_calc}")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
