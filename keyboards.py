from telebot import types

def chooseLevel():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    Button1 = types.KeyboardButton('Уровень 1')
    Button2 = types.KeyboardButton('Уровень 2')
    Button3 = types.KeyboardButton('Уровень 3')
    keyboard.add(Button1, Button2, Button3)
    return keyboard

def checkButton():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard= True, row_width=1)
    Button = types.KeyboardButton('/check')
    keyboard.add(Button)
    return keyboard

def removeKeyboard():
    keyboard = types.ReplyKeyboardRemove()
    return keyboard