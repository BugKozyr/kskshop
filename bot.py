import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import logging
import time

TOKEN = 'vk1.a.bVuQQz3wGe8ySz5valy6jPsDwMvduJML1xwZVFzHpmkKnAZWQzPEwgFZ8bjKUtnsAPygdwuLrSemo1Wra5kZXQe9lFfcdaQRv6N6oEua0bYeYwa_GMJeEzYExIzkdC46GMzytfyZCPI-VWhP8jIvcXRS_kQcHY18jo3j_Y_j9qkmZ1arzkuA87YCSv_QUKdi_4clA1PNPc3K__sdnPqN2A'


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Авторизация в ВКонтакте
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Функция для отправки сообщения с клавиатурой
def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )

# Создание основной клавиатуры
def create_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Узнать о рассрочке', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('График работы', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Помощь', color=VkKeyboardColor.SECONDARY)
    return keyboard

# Создание клавиатуры для подменю "Помощь"
def create_help_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Просит сменить пароль', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Компьютер не включается', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    return keyboard

# Получение имени пользователя
def get_user_name(user_id):
    user_info = vk.users.get(user_ids=user_id)
    if user_info:
        first_name = user_info[0]['first_name']
        return first_name
    return 'друг'

# Основная функция обработки сообщений
def main():
    main_keyboard = create_main_keyboard()
    help_keyboard = create_help_keyboard()
    known_commands = ['начать', 'узнать о рассрочке', 'график работы', 'помощь', 'просит сменить пароль', 'компьютер не включается', 'назад']

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_id = event.user_id
                    message_text = event.text.lower()

                    # Логирование полученного сообщения
                    logging.info(f'Получено сообщение от {user_id}: {message_text}')

                    if message_text not in known_commands:
                        # Если команда неизвестна, ничего не делаем
                        continue

                    if message_text == 'начать':
                        user_name = get_user_name(user_id)
                        send_message(user_id, f'Привет, {user_name}! Чем я могу тебе помочь?', main_keyboard)
                    elif message_text == 'узнать о рассрочке':
                        long_text = (
                            "Онлайн Рассрочка Интернет-Магазин KSKSHOP.RU\n\n"
                            "— Условия —\n"
                            "1. Выдаётся заёмщику с 19 лет.\n"
                            "2. Документы: Паспорт и Снилс.\n"
                            "3. Прописка РФ. Паспорт должен быть действительный.\n"
                            "4. Выдаётся на территории Республика Крым и Севастополь.\n"
                            "__________________________\n"
                            "Процесс оформления онлайн рассрочки:\n"
                            "-> Нужно предоставить данные ФИО заемщика, номер телефона и адрес проживания.\n"
                            "-> Важно! После предоставления ваших данных вы автоматически соглашаетесь на обработку персональных данных.\n"
                            "-> Мы подадим заявку, в течении часа с вами свяжется менеджер банка для подтверждения намерений приобрести товар в рассрочку или кредит.\n"
                            "-> В случае одобрения нужно будет обратиться в ближайшее отделение банка.\n"
                            "-> Доставим в тот же день после одобрения.\n"
                            "__________________________\n"
                            "- В рассрочку товар без учёта скидок и акций, по полной стоимости.\n"
                            "- Полную стоимость товара можете посмотреть у нас на сайте в каталоге или узнать у менеджера по телефону.\n"
                            "- Срок рассрочки до 12 месяцев.\n"
                            "- Доставка нашими курьерами в течении дня.\n"
                            "- Сумма рассрочки от 10 до 150 тыс руб. (Свыше 150 тыс руб нужен будет первоначальный взнос)\n"
                            "- В рассрочку можно оформить любой товар и количество.\n"
                            "- Рассрочку предоставляет партнёр, компания \"ВД Платинум\""
                        )
                        send_message(user_id, long_text)
                    elif message_text == 'график работы':
                        schedule_text = (
                            "Контакты Интернет-магазина KSKSHOP.RU\n\n"
                            "- Мы находимся по адресу: г. Симферополь, Центральный р-н, ул. Крылова, 33\n"
                            "- Рабочий телефон: +7 978 029 02 28\n"
                            "- Рабочий график: Пн - Пт с 10.00 до 20.00 / Сб - Вс с 10.00 до 18.00\n"
                            "- Почта: crimeastokcomputer@inbox.ru"
                        )
                        send_message(user_id, schedule_text)
                    elif message_text == 'помощь':
                        send_message(user_id, 'Какую помощь вам нужно?', help_keyboard)
                    elif message_text == 'просит сменить пароль':
                        password_text = (
                            "При просьбе ввести новый пароль, оставьте поля пустыми и нажмите МЫШКОЙ стрелочку 'Далее'.\n\n"
                            "Это требование операционной системы Windows, наш магазин к этому отношения не имеет."
                        )
                        send_message(user_id, password_text)
                    elif message_text == 'компьютер не включается':
                        send_message(user_id, 'ТЕСТ')
                    elif message_text == 'назад':
                        send_message(user_id, 'Вы вернулись в главное меню.', main_keyboard)
        except requests.exceptions.ConnectionError:
            logging.error('ConnectionError occurred. Reconnecting...')
            time.sleep(5)  # Подождите 5 секунд перед повторным подключением
        except Exception as e:
            logging.exception(f'Unexpected error: {e}')
            time.sleep(5)  # Подождите 5 секунд перед повторным подключением

if __name__ == '__main__':
    main()