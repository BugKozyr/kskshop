import logging
import requests
import base64
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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

# Функция для отправки сообщений с клавиатурой
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    logging.info(f"Сообщение отправлено пользователю {update.effective_chat.id}: {text}")

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
            paid_sum = shipment.get('payedSum', 0) / 100
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Команда /start получена")
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data='today')],
        [InlineKeyboardButton("Вчера", callback_data='yesterday')],
        [InlineKeyboardButton("Неделя", callback_data='week')],
        [InlineKeyboardButton("Месяц", callback_data='month')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите период для статистики продаж:', reply_markup=reply_markup)

async def statms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Команда /statms получена")
    await sales_menu(update, context)

async def sales_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data='today')],
        [InlineKeyboardButton("Вчера", callback_data='yesterday')],
        [InlineKeyboardButton("Неделя", callback_data='week')],
        [InlineKeyboardButton("Месяц", callback_data='month')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(text="Выберите период для статистики продаж:", reply_markup=reply_markup)
    else:
        await update.message.reply_text('Выберите период для статистики продаж:', reply_markup=reply_markup)

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data = query.data
    logging.info(f"Получено событие с данными: {query_data}")

    if query_data == 'today':
        start_date = end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        group_by = 'hour'
    elif query_data == 'yesterday':
        start_date = end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        group_by = 'hour'
    elif query_data == 'week':
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).strftime('%Y-%m-%d')
        group_by = 'day'
    elif query_data == 'month':
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = datetime.datetime.now().replace(day=1).strftime('%Y-%m-%d')
        group_by = 'week'
    elif query_data == 'back':
        await back_to_main_menu(update, context)
        return

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
    if group_by == 'month':
        for key in sorted(stats.keys()):
            stat = stats[key]
            response_message += f'{key} - {stat["count"]} | Сумма: {stat["sum"]:.2f}р | Оплачено: {stat["paid_sum"]:.2f}р\n'
    else:
        for key in sorted(stats.keys()):
            stat = stats[key]
            response_message += f'{key} - {stat["count"]} | Сумма: {stat["sum"]:.2f}р | Оплачено: {stat["paid_sum"]:.2f}р\n'
    await query.edit_message_text(text=response_message)
    await sales_menu(update, context)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("statms", statms))
    application.add_handler(CallbackQueryHandler(button))

    logging.info("Бот запущен и готов к работе")
    application.run_polling()

if __name__ == '__main__':
    main()
