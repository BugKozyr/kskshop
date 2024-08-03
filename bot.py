import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import logging
import time
import requests
from datetime import datetime, timedelta

TOKEN_GROUP = 'vk1.a.bIduXhrbRQiKbqusyNrJ-Yem2NNRLaUNB_UViX6Noh91QLsU3etlAaFjzEFpBVlo4HREnNbAtloWLjSwVSMxEsXkjnOA-h6R5GWmmq_k3yO_SNEj6ztFBNqk9OwHIip3L66hH2VKyc2vjMHZtkLeSCHO6IhQuoX_lo01Ab_VteU0dWjZmPE7sZnIX7pBxusE5O4Y5DEIgHuAVnTGPcRWzQ'
TOKEN_USER = 'vk1.a.s3jQhza_ZB_PVmxEgk4Jp6jkPaNWmNVBah_d-jf-mQmMmA53fwArMWlNd6OWIKekRP0HBmqnsMvBmsGDVFFfsZshv273AlTIRdnR20GizSMsrU0tBE0AjQSYwq0CMz3A6iiGPtBoL5SeuedApw7OkcuSHvblGPTXTXu1-shk4c_ybRQ7_JS3EOHqBFB5C8znsvH8NLu49vQHiGZ5vdxpLg'  # Токен пользователя с правами администратора
PHOTO_PATH = 'cable.jpg'
RAFFLE_PHOTO_PATH = 'mon.jpg'  # Убедитесь, что указанный путь правильный и файл существует
WEBSITE_URL = 'https://kskshop.ru/configuratorpc/'
WILDBERRIES_URL = 'https://www.wildberries.ru/brands/kskshop'
RAFFLE_URL = 'https://vk.com/wall-35493903_3078'
ADMIN_IDS = [146880457, 25510716]  # Список ID администраторов группы
GROUP_ID = '35493903'
POST_ID = '3078'
END_DATE = datetime(2024, 8, 21, 20, 0, 0)  # Установите дату и время окончания розыгрыша

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Авторизация в API ВКонтакте для группы
vk_session_group = vk_api.VkApi(token=TOKEN_GROUP)
vk_group = vk_session_group.get_api()
longpoll = VkLongPoll(vk_session_group)

# Авторизация в API ВКонтакте для пользователя
vk_session_user = vk_api.VkApi(token=TOKEN_USER)
vk_user = vk_session_user.get_api()

# Функция для отправки сообщения с клавиатурой
def send_message(user_id, message, keyboard=None):
    vk_group.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )

# Функция для отправки сообщения с фотографией
def send_photo_message(user_id, message, photo_path, keyboard=None):
    upload = vk_api.VkUpload(vk_session_group)
    photo = upload.photo_messages(photo_path)
    owner_id = photo[0]['owner_id']
    photo_id = photo[0]['id']
    attachment = f'photo{owner_id}_{photo_id}'
    vk_group.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        attachment=attachment,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )

# Функция для отправки пустой клавиатуры (удаление клавиатуры)
def send_empty_keyboard(user_id):
    empty_keyboard = VkKeyboard.get_empty_keyboard()
    vk_group.messages.send(
        user_id=user_id,
        message="Обновление клавиатуры...",
        random_id=0,
        keyboard=empty_keyboard
    )

# Функция для получения статистики группы
def get_group_stats():
    try:
        now = datetime.now()
        remaining_time = END_DATE - now
        if remaining_time.total_seconds() > 0:
            days, seconds = remaining_time.days, remaining_time.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
        else:
            days, hours, minutes, seconds = 0, 0, 0, 0

        # Получаем общую информацию о группе
        group_info = vk_user.groups.getById(group_id=GROUP_ID, fields='members_count')[0]
        members_count = group_info['members_count']

        # Получаем статистику для определенной записи
        post_stats = vk_user.wall.getById(posts=f'-{GROUP_ID}_{POST_ID}')[0]
        post_views = post_stats['views']['count']
        post_likes = post_stats['likes']['count']
        post_reposts = post_stats['reposts']['count']

        # Формируем сообщение со статистикой
        message = (
            f"Количество участников: {members_count}\n"
            "-------------------\n"
            f"Розыгрыш: {post_views} просмотров | {post_likes} лайков | {post_reposts} репостов\n"
            f"До конца розыгрыша осталось: {days} дней, {hours} часов, {minutes} минут, {seconds} секунд"
        )

        logging.info(message)
        return message

    except requests.exceptions.RequestException as e:
        logging.error(f"Произошла ошибка при соединении: {e}")
        return "Произошла ошибка при соединении."
    except vk_api.exceptions.VkApiError as e:
        logging.error(f"Произошла ошибка VK API: {e}")
        return "Произошла ошибка VK API."

# Создание основной клавиатуры
def create_main_keyboard(user_id):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('МОНИТОР ЗА РЕПОСТ', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Каталог', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Узнать о рассрочке', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('График работы', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # Переход на новую строку
    keyboard.add_button('Часто задаваемые вопросы', color=VkKeyboardColor.SECONDARY)

    if user_id not in ADMIN_IDS:
        keyboard.add_line()  # Кнопки не отображаются для администраторов
        keyboard.add_openlink_button('Конфигуратор ПК', link=WEBSITE_URL)  # Кнопка для перехода на сайт
        keyboard.add_openlink_button('Мы на Wildberries', link=WILDBERRIES_URL)  # Кнопка для перехода на Wildberries

    if user_id in ADMIN_IDS:
        keyboard.add_line()
        keyboard.add_button('Статистика', color=VkKeyboardColor.PRIMARY)

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

# Создание inline клавиатуры для участия в розыгрыше
def create_inline_raffle_keyboard():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_openlink_button('Принять участие', link=RAFFLE_URL)
    return keyboard

# Создание inline клавиатуры для покупки ключа
def create_inline_buy_key_keyboard():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Купить ключ', color=VkKeyboardColor.POSITIVE, payload={"command": "buy_key"})
    return keyboard

# Создание inline клавиатуры для перехода в диалог
def create_inline_dialog_keyboard(user_id):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_openlink_button('Перейти в диалог', link=f'https://vk.com/gim35493903?sel={user_id}')
    return keyboard

# Получение имени пользователя
def get_user_name(user_id):
    user_info = vk_user.users.get(user_ids=user_id)
    if user_info:
        first_name = user_info[0]['first_name']
        return first_name
    return 'друг'

# Функция для отправки уведомления администраторам
def notify_admins(user_id, user_name):
    for admin_id in ADMIN_IDS:
        admin_message = f"{user_name} хочет купить ключ"
        keyboard = create_inline_dialog_keyboard(user_id)
        send_message(admin_id, admin_message, keyboard)

# Основная функция обработки сообщений
def main():
    catalog_keyboard = create_catalog_keyboard()
    components_keyboard = create_components_keyboard()
    help_keyboard = create_help_keyboard()
    inline_raffle_keyboard = create_inline_raffle_keyboard()
    inline_buy_key_keyboard = create_inline_buy_key_keyboard()
    known_commands = [
        'начать', 'узнать о рассрочке', 'график работы', 'часто задаваемые вопросы', 
        'windows требует сменить пароль', 'компьютер не включается', 'как активировать windows', 'назад', 'каталог', 'комплектующие', 'купить ключ', 'монитор за репост', 'статистика'
    ]

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_id = event.user_id
                    message_text = event.text.lower()

                    # Логирование полученного сообщения
                    logging.info(f'Получено сообщение от {user_id}: {message_text}')

                    if message_text not in known_commands and user_id not in ADMIN_IDS:
                        # Если команда неизвестна и пользователь не администратор, ничего не делаем
                        continue

                    main_keyboard = create_main_keyboard(user_id)

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
                        notify_admins(user_id, user_name)
                        send_message(user_id, "Ваш запрос отправлен администратору.")
                    elif message_text == 'каталог':
                        send_message(user_id, 'Выберите категорию:', catalog_keyboard)
                    elif message_text == 'комплектующие':
                        send_message(user_id, 'Выберите категорию комплектующих:', components_keyboard)
                    elif message_text == 'монитор за репост':
                        raffle_text = (
                            "Разыгрываем игровой монитор Xiaomi G24 165Hz за репост!\n"
                            "Итоги будут подведены 21.08.2024 в 20:00."
                        )
                        send_photo_message(user_id, raffle_text, RAFFLE_PHOTO_PATH, inline_raffle_keyboard)
                    elif message_text == 'статистика' and user_id in ADMIN_IDS:
                        stats_message = get_group_stats()
                        send_message(user_id, stats_message)
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
