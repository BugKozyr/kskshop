import requests
import base64
import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Токены доступа
TELEGRAM_TOKEN = '7487257526:AAFthWX-2bavuX6TAi5XNCr5_7-D6GRXrRU'
MOYSKLAD_LOGIN = '79816826150@crimeastokcomputer'
MOYSKLAD_PASSWORD = '2001v1974XD'

# Функция для получения токена Мой Склад
def get_moysklad_token():
    try:
        response = requests.post(
            'https://api.moysklad.ru/api/remap/1.2/security/token',
            headers={
                'Authorization': 'Basic ' + base64.b64encode(f"{MOYSKLAD_LOGIN}:{MOYSKLAD_PASSWORD}".encode()).decode(),
                'Accept-Encoding': 'gzip'
            }
        )
        response.raise_for_status()
        logging.info("Токен Мой Склад успешно получен")
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения токена Мой Склад: {e}")
        return None

MOYSKLAD_TOKEN = get_moysklad_token()

def get_shipments_statistics(moysklad_token, start_date, end_date, group_by='hour'):
    try:
        response = requests.get(
            f'https://api.moysklad.ru/api/remap/1.2/entity/demand?filter=moment>{start_date} 00:00:00;moment<{end_date} 23:59:59',
            headers={
                'Authorization': f'Bearer {moysklad_token}',
                'Accept-Encoding': 'gzip'
            }
        )
        response.raise_for_status()
        shipments = response.json().get('rows', [])
        
        total_sum = 0
        total_paid_sum = 0
        stats = {}

        for shipment in shipments:
            shipment_time_str = shipment['moment']
            logging.info(f"Обработка отгрузки с моментом: {shipment_time_str}")
            shipment_time = datetime.datetime.strptime(shipment_time_str, '%Y-%m-%d %H:%M:%S.%f')
            
            if group_by == 'hour':
                group_key = shipment_time.strftime('%H:00')
            elif group_by == 'day':
                group_key = shipment_time.strftime('%d.%m.%Y')
            elif group_by == 'week':
                week_start = (shipment_time - datetime.timedelta(days=shipment_time.weekday())).strftime('%d.%m.%Y')
                week_end = (shipment_time + datetime.timedelta(days=6-shipment_time.weekday())).strftime('%d.%m.%Y')
                group_key = f'{week_start} - {week_end}'
            elif group_by == 'month':
                group_key = shipment_time.strftime('%m.%Y')
            
            shipment_sum = shipment['sum'] / 100
            paid_sum = shipment.get('payedSum', 0) / 100  # Используем 'payedSum' для оплаченной суммы
            total_sum += shipment_sum
            total_paid_sum += paid_sum

            if group_key not in stats:
                stats[group_key] = {'count': 0, 'sum': 0, 'paid_sum': 0}
            
            stats[group_key]['count'] += 1
            stats[group_key]['sum'] += shipment_sum
            stats[group_key]['paid_sum'] += paid_sum

        logging.info(f"Статистика отгрузок за период {start_date} - {end_date} получена успешно")
        return len(shipments), total_sum, total_paid_sum, stats
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка получения статистики отгрузок: {e}")
        return 0, 0, 0, {}

def start(update: Update, context: CallbackContext) -> None:
    logging.info("Команда /start получена")
    keyboard = [
        [
            InlineKeyboardButton("Сегодня", callback_data='today'),
            InlineKeyboardButton("Вчера", callback_data='yesterday')
        ],
        [
            InlineKeyboardButton("Неделя", callback_data='week'),
            InlineKeyboardButton("Месяц", callback_data='month')
        ],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите период для статистики продаж:', reply_markup=reply_markup)

def sales_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Сегодня", callback_data='today'),
            InlineKeyboardButton("Вчера", callback_data='yesterday')
        ],
        [
            InlineKeyboardButton("Неделя", callback_data='week'),
            InlineKeyboardButton("Месяц", callback_data='month')
        ],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите период для статистики продаж:", reply_markup=reply_markup)

def back_to_main_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    start(update, context)

def handle_date_range(update: Update, context: CallbackContext, start_date: str, end_date: str, group_by: str) -> None:
    logging.info(f"Обработка статистики с {start_date} по {end_date}")
    shipment_count, total_sum, total_paid_sum, stats = get_shipments_statistics(MOYSKLAD_TOKEN, start_date, end_date, group_by)
    response_message = (
        f'Статистика с {start_date} по {end_date}:\n'
        f'-----\n'
        f'Отгрузок: {shipment_count}\n'
        f'-----\n'
        f'Сумма: {total_sum:.2f}р\n'
        f'Оплаченная сумма: {total_paid_sum:.2f}р\n'
        f'-----\n'
    )
    if group_by == 'week':
        for key in sorted(stats.keys()):
            stat = stats[key]
            response_message += f'{key} - {stat["count"]} | Сумма: {stat["sum"]:.2f}р | Оплачено: {stat["paid_sum"]:.2f}р\n'
    else:
        for key in sorted(stats.keys()):
            stat = stats[key]
            response_message += f'{key} - {stat["count"]} | Сумма: {stat["sum"]:.2f}р | Оплачено: {stat["paid_sum"]:.2f}р\n'
    
    keyboard = [[InlineKeyboardButton("Назад", callback_data='sales')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text=response_message, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query_data = query.data
    logging.info(f"Получено событие с данными: {query_data}")

    if query_data == 'sales':
        sales_menu(update, context)
    elif query_data == 'back':
        back_to_main_menu(update, context)
    elif query_data == 'today':
        start_date = end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        handle_date_range(update, context, start_date, end_date, 'hour')
    elif query_data == 'yesterday':
        start_date = end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        handle_date_range(update, context, start_date, end_date, 'hour')
    elif query_data == 'week':
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).strftime('%Y-%m-%d')
        handle_date_range(update, context, start_date, end_date, 'day')
    elif query_data == 'month':
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = datetime.datetime.now().replace(day=1).strftime('%Y-%m-%d')
        handle_date_range(update, context, start_date, end_date, 'week')

def statms(update: Update, context: CallbackContext) -> None:
    logging.info("Команда /statms получена")
    keyboard = [
        [
            InlineKeyboardButton("Сегодня", callback_data='today'),
            InlineKeyboardButton("Вчера", callback_data='yesterday')
        ],
        [
            InlineKeyboardButton("Неделя", callback_data='week'),
            InlineKeyboardButton("Месяц", callback_data='month')
        ],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите период для статистики продаж:', reply_markup=reply_markup)

def main() -> None:
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("statms", statms))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Постоянная кнопка "Статистика" в нижнем меню
    reply_keyboard = [['/statms']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    dispatcher.bot.set_my_commands([('statms', 'Показать статистику')])

    logging.info("Бот запущен и готов к работе")

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
