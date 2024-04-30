import pygame


import telebot


from telebot import types


bot = telebot.TeleBot('6204607117:AAHbJAytVVF8pYg-ocNwN_gUP5Ewono-ogs')

time = '6:00'

dawn = False

flag = True

pygame.init()
main_music = 'alarm.mp3'
download_music = ''
pygame.mixer.music.load('alarm.mp3')


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Приветствую, {message.from_user.first_name}. Я - бот, '
                                      f'чье существование предназначено для настройки твоего будильника.'
                                      f' Через меня ты можешь настроить базовые функции будильника.'
                                      f' Для того, чтобы узнать мои возможности, введи команду /help')


@bot.message_handler(commands=['help'])
def help_main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Установить время срабатывания будильника', callback_data='set_time'))
    btn1 = types.InlineKeyboardButton('Включить "Рассвет"', callback_data='dawn_on')
    btn2 = types.InlineKeyboardButton('Отключить "Рассвет"', callback_data='dawn_off')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, '''Команды будильника:
    /help - справочник команд для работы с ботом
    /start - начало работы с ботом
    /set_time - установить время срабатывания будильника
    /dawn_on - включить функцию "Рассвет"
    /dawn_off - отключить функцию "Рассвет"
    /set_main_music - сбросить мелодию до мелодии по-умолчанию
ПРИМЕЧАНИЕ: Для установки собственной мелодии будильника надо отправить аудио файл боту
    ''', reply_markup=markup)


@bot.message_handler(commands=['set_time'])
def set_time(message):
    bot.send_message(message.chat.id, 'Введите время (формат ЧЧ:ММ)')
    bot.register_next_step_handler(message, get_time)


@bot.message_handler(commands=['set_main_music'])
def set_main_music(message):
    global download_music
    bot.send_message(message.chat.id, 'Вы установили мелодию по-умолчанию.')
    download_music = ''
    pygame.mixer.music.load('alarm.mp3')


def get_time(message):
    global time
    n_time = message.text
    try:
        if len(n_time.split(':')) == 2:
            n1 = str(int(n_time.split(':')[0]))
            n2 = str(int(n_time.split(':')[1]))

            if int(n1) > 23 or int(n1) < 0:
                raise Exception
            if int(n2) > 59 or int(n2) < 0:
                raise Exception

            if len(n1) > 2:
                raise Exception
            if len(n2) == 1:
                n2 = f'0{n2}'
            elif len(n2) > 2:
                raise Exception
            time = f'{n1}:{n2}'
            bot.send_message(message.chat.id, f'Будильник установлен на {time}')
        else:
            raise Exception
    except Exception:
        bot.send_message(message.chat.id, 'Неправильный формат ввода. Попробуйте снова(/set_time)')


@bot.message_handler(commands=['dawn_on'])
def dawn_true(message):
    global dawn
    bot.send_message(message.chat.id, 'Вы включили функцию рассвет')
    dawn = True


@bot.message_handler(content_types=['document', 'audio'])
def get_file(message):
    global download_music
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да', callback_data='yes')
    btn2 = types.InlineKeyboardButton('Нет', callback_data='no')
    markup.row(btn1, btn2)
    try:
        if message.content_type == 'audio':  # mp3


            file_info = bot.get_file(message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = message.audio.file_name
            if src == main_music:
                raise TypeError
            if src == download_music:
                raise NameError
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            download_music = src
            bot.reply_to(message, f"Установить мелодию {src[:-4]}?", reply_markup=markup)
    except TypeError:
        bot.reply_to(message, 'Измените название мелодии на другое и попробуйте снова.')
    except NameError:
        bot.reply_to(message, 'Мелодия уже установлена.')
    except Exception as e:
        bot.reply_to(message, str(e))


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    global download_music
    if callback.data == 'yes':
        confirm(download_music, callback.message.chat.id)
        bot.delete_message(callback.message.chat.id, callback.message.id)
    if callback.data == 'no':
        bot.send_message(callback.message.chat.id, f'Отменено.')
        download_music = ''
        bot.delete_message(callback.message.chat.id, callback.message.id)
    if callback.data == 'set_time':
        set_time(callback.message)
    if callback.data == 'dawn_on':
        dawn_true(callback.message)
    if callback.data == 'dawn_off':
        dawn_false(callback.message)


def confirm(file, id):
    try:
        pygame.mixer.music.load(file)
        bot.send_message(id, f'Вы установили мелодию {download_music[:-4]}.')
    except Exception:
        bot.send_message(id, 'Неправильный формат файла, попробуйте другой')


@bot.message_handler(commands=['dawn_off'])
def dawn_false(message):
    global dawn
    bot.send_message(message.chat.id, 'Вы отключили функцию рассвет')
    dawn = False


@bot.message_handler(commands=['play_music'])
def play(message):
    pygame.mixer.music.play(-1)


@bot.message_handler(commands=['stop_music'])
def stop(message):
    pygame.mixer.music.stop()


bot.polling(non_stop=True)
