import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import logging
import time
import requests

TOKEN = 'vk1.a.bIduXhrbRQiKbqusyNrJ-Yem2NNRLaUNB_UViX6Noh91QLsU3etlAaFjzEFpBVlo4HREnNbAtloWLjSwVSMxEsXkjnOA-h6R5GWmmq_k3yO_SNEj6ztFBNqk9OwHIip3L66hH2VKyc2vjMHZtkLeSCHO6IhQuoX_lo01Ab_VteU0dWjZmPE7sZnIX7pBxusE5O4Y5DEIgHuAVnTGPcRWzQ'
PHOTO_PATH = 'cable.jpg'
WEBSITE_URL = 'https://kskshop.ru/configuratorpc/'
WILDBERRIES_URL = 'https://www.wildberries.ru/brands/kskshop'
RAFFLE_URL = 'https://vk.com/wall-35493903_3078'
ADMIN_IDS = [146880457, 242434059]  # Список ID администраторов группы

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

# Функция для отправки сообщения с фотографией
def send_photo_message(user_id, message, photo_path, keyboard=None):
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo_messages(photo_path)
    owner_id = photo[0]['owner_id']
    photo_id = photo[0]['id']
    attachment = f'photo{owner_id}_{photo_id}'
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        attachment=attachment,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )

# Функция для отправки пустой клавиатуры (удаление клавиатуры)
def send_empty_keyboard(user_id):
    empty_keyboard = VkKeyboard.get_empty_keyboard()
    vk.messages.send(
        user_id=user_id,
        message="Обновление клавиатуры...",
        random_id=0,
        keyboard=empty_keyboard
    )

# Создание основной клавиатуры
def create_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_openlink_button('РОЗЫГРЫШ МОНИТОРА', link=RAFFLE_URL)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Каталог', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Узнать о рассрочке', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('График работы', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Часто задаваемые вопросы', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Конфигуратор ПК', link=WEBSITE_URL)  # Кнопка для перехода на сайт
    keyboard.add_openlink_button('Мы на Wildberries', link=WILDBERRIES_URL)  # Кнопка для перехода на Wildberries
    return keyboard

# Создание клавиатуры для каталога
def create_catalog_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_openlink_button('Игровые компьютеры', link='https://vk.com/market-35493903?section=album_36')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Мониторы', link='https://vk.com/market-35493903?section=album_1')
    keyboard.add_openlink_button('Мышки', link='https://vk.com/market-35493903?section=album_5')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Клавиатуры', link='https://vk.com/market-35493903?section=album_30')
    keyboard.add_openlink_button('Наушники', link='https://vk.com/market-35493903?section=album_31')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Комплектующие', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    return keyboard

# Создание клавиатуры для комплектующих
def create_components_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_openlink_button('Процессоры', link='https://vk.com/market-35493903?section=album_12')
    keyboard.add_openlink_button('Видеокарты', link='https://vk.com/market-35493903?section=album_38')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Материнские платы', link='https://vk.com/market-35493903?section=album_39')
    keyboard.add_openlink_button('Оперативная память', link='https://vk.com/market-35493903?section=album_21')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Блоки питания', link='https://vk.com/market-35493903?section=album_18')
    keyboard.add_openlink_button('SSD накопители', link='https://vk.com/market-35493903?section=album_34')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_openlink_button('Корпуса', link='https://vk.com/market-35493903?section=album_19')
    keyboard.add_openlink_button('Охлаждение', link='https://vk.com/market-35493903?section=album_23')
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    return keyboard

# Создание клавиатуры для подменю "Помощь"
def create_help_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Windows требует сменить пароль', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Компьютер не включается', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Как активировать Windows', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    return keyboard

# Создание inline клавиатуры для покупки ключа
def create_inline_buy_key_keyboard():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Купить ключ', color=VkKeyboardColor.POSITIVE)
    return keyboard

# Получение имени пользователя
def get_user_name(user_id):
    user_info = vk.users.get(user_ids=user_id)
    if user_info:
        first_name = user_info[0]['first_name']
        return first_name
    return 'друг'

# Функция для отправки уведомления администраторам
def notify_admins(message):
    for admin_id in ADMIN_IDS:
        send_message(admin_id, message)

# Основная функция обработки сообщений
def main():
    main_keyboard = create_main_keyboard()
    catalog_keyboard = create_catalog_keyboard()
    components_keyboard = create_components_keyboard()
    help_keyboard = create_help_keyboard()
    inline_buy_key_keyboard = create_inline_buy_key_keyboard()
    known_commands = [
        'начать', 'узнать о рассрочке', 'график работы', 'часто задаваемые вопросы', 
        'windows требует сменить пароль', 'компьютер не включается', 'как активировать windows', 'назад', 'каталог', 'комплектующие', 'купить ключ'
    ]

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
                        send_message(user_id, f'Привет, {user_name}! Напишите ваше сообщение и оператор ответит в течении нескольких минут!)', main_keyboard)
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
                            "Контакты Интернет-магазина KSKSHOP.RU\n"
                            "- Мы находимся по адресу: г. Симферополь, Центральный р-н, ул. Крылова, 33\n"
                            "- Рабочий график: Пн - Пт с 10.00 до 20.00 / Сб - Вс с 10.00 до 18.00\n"
                             "__________________________\n"
                            "- Рабочий телефон: +7 978 029 02 28\n"
                            "- Почта: crimeastokcomputer@inbox.ru"
                        )
                        send_message(user_id, schedule_text)
                    elif message_text == 'часто задаваемые вопросы':
                        send_message(user_id, 'Если нет нужного вопроса, менеджер ответит вам ближайшее время', help_keyboard)
                    elif message_text == 'windows требует сменить пароль':
                        password_text = (
                            "При просьбе ввести новый пароль, оставьте поля пустыми и нажмите МЫШКОЙ стрелочку 'Далее'.\n"
                            "Это требование операционной системы Windows, наш магазин к этому отношения не имеет."
                        )
                        send_message(user_id, password_text)
                    elif message_text == 'компьютер не включается':
                        help_text = (
                            "1. Проверьте, правильно ли вы подключили монитор к системному блоку. Монитор должен быть подключен к видеокарте, а не материнской плате.\n"
                            "Если на мониторе и видеокарте отличаются разъемы, необходимо приобрести адаптер VGA-HDMI / VGA-DVI.\n"
                             "__________________________\n"
                            "2. Проверьте работоспособность розетки. Попробуйте подключить компьютер в другую розетку или сетевой фильтр."
                        )
                        send_photo_message(user_id, help_text, PHOTO_PATH, help_keyboard)
                    elif message_text == 'как активировать windows':
                        activation_text = (
                            "Мы устанавливаем официальный, но не активированный образ Windows.\n"
                            "В нашем магазине есть возможность приобрести лицензионный ключ для Windows 10 и Windows 11, а также ключ активации для Microsoft Office 2016.\n"
                            "-----------------------\n"
                            "Ключ активации Windows - 1.000 рублей\n"
                            "Ключ активации Microsoft Office 2016 - 2.000 рублей"
                        )
                        send_message(user_id, activation_text, inline_buy_key_keyboard)
                    elif message_text == 'купить ключ':
                        user_name = get_user_name(user_id)
                        notify_admins(f"{user_name} хочет купить ключ")
                        send_message(user_id, "Ваш запрос отправлен администратору.")
                    elif message_text == 'каталог':
                        send_message(user_id, 'Выберите категорию:', catalog_keyboard)
                    elif message_text == 'комплектующие':
                        send_message(user_id, 'Выберите категорию комплектующих:', components_keyboard)
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
