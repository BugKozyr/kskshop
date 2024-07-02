import vk_api
import datetime
import time
from vk_api.utils import get_random_id

# Ваш токен доступа
TOKEN = 'vk1.a.bIduXhrbRQiKbqusyNrJ-Yem2NNRLaUNB_UViX6Noh91QLsU3etlAaFjzEFpBVlo4HREnNbAtloWLjSwVSMxEsXkjnOA-h6R5GWmmq_k3yO_SNEj6ztFBNqk9OwHIip3L66hH2VKyc2vjMHZtkLeSCHO6IhQuoX_lo01Ab_VteU0dWjZmPE7sZnIX7pBxusE5O4Y5DEIgHuAVnTGPcRWzQ'
ADMIN_USER_ID = '146880457'  # ID администратора для отправки напоминаний
CHECK_INTERVAL = 900  # 15 минут в секундах

# Авторизация в ВКонтакте
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

def send_reminder(admin_id, user_id):
    user_info = vk.users.get(user_ids=user_id)
    user_name = user_info[0]['first_name'] if user_info else 'пользователь'
    message = f'Сообщение от {user_name} не отвечено!'
    vk.messages.send(
        user_id=admin_id,
        message=message,
        random_id=get_random_id()
    )

def check_unread_messages():
    now = datetime.datetime.now()
    moscow_time = now + datetime.timedelta(hours=3)
    if 10 <= moscow_time.hour < 21:
        conversations = vk.messages.getConversations(filter='unanswered')['items']
        for conversation in conversations:
            last_message = conversation['last_message']
            message_time = datetime.datetime.fromtimestamp(last_message['date'])
            time_diff = now - message_time
            if time_diff.total_seconds() > CHECK_INTERVAL:
                send_reminder(ADMIN_USER_ID, last_message['from_id'])

if __name__ == '__main__':
    while True:
        check_unread_messages()
        time.sleep(CHECK_INTERVAL)
