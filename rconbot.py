import telebot
import settings
import sqlite3 as sql
import keyboards as kb
import random
import json
import requests
import os
from mcrcon import MCRcon

bot = telebot.TeleBot(settings.token)

if not os.path.isdir('UserData'):
    os.mkdir('UserData')

database = sql.connect('UserData/donate.db', check_same_thread=False)
cur = database.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users (
    chat_id INT PRIMARY KEY,
    nickname VARCHAR,
    level VARCHAR,
    comment VARCHAR,
    amount INT,
    expired VARCHAR
)''')
database.commit()

@bot.message_handler(content_types=['text'])
def donate(message):
    if message.text == '/donate':
        print('Code 1')
        bot.send_message(message.from_user.id, "Введите ваш ник на сервере.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, get_nickname)
    elif message.text == '/check':
        print('Code 2')
        status = False
        userID = message.from_user.id
        cur.execute(f"SELECT comment FROM users WHERE chat_id = '{userID}'")
        commentUser = cur.fetchone()
        cur.execute(f"SELECT level FROM users WHERE chat_id = {userID}")
        userLevel = cur.fetchone()
        cur.execute(f"SELECT amount FROM users WHERE chat_id = {userID}")
        amountUser = cur.fetchone()
        cur.execute(f"SELECT nickname FROM users WHERE chat_id = {userID}")
        nickname = cur.fetchone()
        api_access_token = settings.qiwi_token
        my_login = settings.qiwi_number
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + api_access_token  
        parameters = {'rows': '15'}
        h = s.get('https://edge.qiwi.com/payment-history/v1/persons/'+my_login+'/payments', params = parameters)
        hist = json.loads(h.text)
        for i in range(14):
            commentQiwi=hist['data'][i]['comment']
            amountQiwi = hist['data'][i]['sum']['amount']
            if commentQiwi == commentUser[0]:
                print('Есть совпадение, проверяем сумму')
                if amountQiwi == amountUser[0]:
                    print('Всё окей, выдаём донат')
                    try:
                        mc = MCRcon(settings.ip, settings.password, port=25575)
                        mc.connect()
                        mc.command(f'say {nickname} Получил уровень {userLevel[0]}')
                        mc.command(f'lp user {nickname} group set {settings.priv[int(userLevel[0])]}')
                        mc.disconnect()
                        status = True
                        break
                    except ConnectionRefusedError as error:
                        bot.send_message(userID, 'В данный момент подключение к серверу недоступно. Перешлите следующее сообщение администратору и повторите попытку позже.')
                        bot.send_message(userID, error)
                        status = False
                        break
                else:
                    print('Сумма не сошлась')
                    status = False
            else:
                print('Запись не найдена')
                status = False
        if status == True:
            bot.send_message(userID, 'Оплата прошла, донат выдан.')
            bot.register_next_step_handler_by_chat_id(userID, donate)
        elif status == False:
            bot.send_message(userID, 'Повторная проверка будет доступна через минуту.')
            bot.register_next_step_handler_by_chat_id(userID,donate)

def get_nickname(message):  #Требует доработкиa с доплатой
    chat_id = message.from_user.id
    nickname = message.text
    if len(nickname) >0:
        cur.execute(f"SELECT chat_id FROM users WHERE chat_id = '{chat_id}'")
        variable = cur.fetchone()
        cur.execute(f"SELECT chat_id FROM users WHERE chat_id = '{chat_id}'")
        if variable is None:
            cur.execute(f"INSERT INTO users(chat_id,nickname) VALUES (?,?)", (chat_id,nickname))
            database.commit()
            bot.send_message(chat_id, 'Выберите желаемую привилегию', reply_markup=kb.chooseLevel())
            bot.register_next_step_handler_by_chat_id(chat_id, get_level)
        elif variable[0] == chat_id:
            cur.execute(f"SELECT nickname FROM users WHERE chat_id = '{chat_id}'")
            nick = cur.fetchone()
            if nickname == nick[0]:
                bot.send_message(chat_id, 'Похоже, вы хотите сделать доплату...', reply_markup=kb.chooseLevel())
                bot.register_next_step_handler_by_chat_id(chat_id, get_level)
            else:
                cur.execute("UPDATE users SET nickname = ? WHERE chat_id = ?", (nickname,chat_id))
                bot.send_message(chat_id, 'Выберите желаемую привилегию', reply_markup=kb.chooseLevel())
                bot.register_next_step_handler_by_chat_id(chat_id, get_level)

def get_level(message):
    chat_id = message.from_user.id
    level = message.text
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
    random.shuffle(chars)
    comment = ''.join([random.choice(chars) for x in range(10)]).replace('\n','D')
    if (str(level) == 'Уровень 1' or str(level) == 'Уровень 2' or str(level) == 'Уровень 3'):
        cur.execute(f"UPDATE users SET level = ? WHERE chat_id = ?", (level,chat_id))
        cur.execute(f"UPDATE users SET comment = ? WHERE chat_id = ?", (comment, chat_id))
        if level == 'Уровень 1':
            amount = 1
        if level == 'Уровень 2':
            amount = 2
        if level == 'Уровень 3':
            amount = 3
        bot.send_message(chat_id, f'''К оплате {amount} рублей. Оплата производится через QIWI по никнейму.
В поле "Никнейм получателя укажите TWILIGHTPROJECT.\nОбязательно укажите в комментарии: {comment}
После оплаты нажмите на кнопку /check
Учтите, что на 1 аккаунт Telegram привязывается только 1 игровой профиль на сервере. В случае, если вы зохотите''', reply_markup=kb.checkButton())
        cur.execute(f"UPDATE users SET amount = ? WHERE chat_id = ?", (int(amount),chat_id))
        database.commit()
        bot.register_next_step_handler_by_chat_id(chat_id, donate)
    else:
        bot.send_message(chat_id, 'Пожалуйста, выберите уровень с клавиатуры!')
        bot.register_next_step_handler_by_chat_id(chat_id, get_level)

bot.polling(none_stop=True, interval=0, skip_pending=True)