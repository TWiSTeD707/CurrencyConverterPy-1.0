import requests

def get_exchange_rate(target_currency):
    """Получение курса валюты с сайта ЦБ РФ."""
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'  # URL API ЦБ РФ
    response = requests.get(url)
    data = response.json()  # Преобразование ответа в JSON
    try:
        exchange_rate = data['Valute'][target_currency]['Value']  # Получение курса валюты
    except KeyError:
        return "Ошибка: Неправильный код валюты."  # Возврат ошибки, если валюта не найдена
    return exchange_rate

def convert_currency(amount, target_currency):
    """Конвертация валюты в рубли."""
    exchange_rate = get_exchange_rate(target_currency)  # Получение курса
    if isinstance(exchange_rate, str):
        return exchange_rate  # Возврат ошибки, если курс не был получен
    return amount * exchange_rate  # Вычисление конвертированной суммы