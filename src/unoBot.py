import telebot
import logic
import sharedVars
import time
from telebot.apihelper import ApiTelegramException
from telebot import types

bot = telebot.TeleBot('Your-Tg-Bot-ID')

def safe_send_message(chat_id, text, reply_markup=None, retries=3):
    for attempt in range(retries):
        try:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        except ApiTelegramException as e:
            if e.error_code == 429 and 'retry after' in str(e):
                wait_time = int(str(e).split('retry after ')[1])
                time.sleep(wait_time + 1)  # Добавляем 1 секунду для надежности
            else:
                raise
    raise Exception(f"Failed to send message after {retries} attempts")


def safe_send_stiker(chat_id, stiker, retries=3):
    for attempt in range(retries):
        try:
            return bot.send_sticker(chat_id, stiker)
        except ApiTelegramException as e:
            if e.error_code == 429 and 'retry after' in str(e):
                wait_time = int(str(e).split('retry after ')[1])
                time.sleep(wait_time + 1)  # Добавляем 1 секунду для надежности
            else:
                raise
    raise Exception(f"Failed to send sticker after {retries} attempts")


@bot.message_handler(commands=['start'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['start_game'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['stats'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['stiker'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['end_game'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['admin'])
def main(info):
    sharedVars.st.put(info)


def admin(info):
    '''Вывод информации о создателях.'''
    safe_send_message(
        info.chat.id,
        'Писать по всем вопросам:@rbedin25, @shout_0_0, @n3tw4lk3r')


@bot.message_handler(commands=['help'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['help_game'])
def main(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['join'])
def message_reply(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['play'])
def message_reply(info):
    sharedVars.st.put(info)


@bot.message_handler(commands=['clear'])
def message_reply(info):
    sharedVars.st.put(info)


@bot.message_handler(content_types='text')
def message_reply(info):
    if info.text == "Присоединиться":
        sharedVars.st.put(info)

    if info.text == "Начать игру":
        sharedVars.st.put(info)

    if info.chat.id in logic.games_byId and logic.games_byId[
            info.chat.id].isRunning:
        player = info.from_user.username

        if (info.text == "Взять карту" or info.text == "Пропуск хода"
            ) and logic.games_byId[info.chat.id].players[logic.games_byId[
                info.chat.id].current_position].name == player:
            sharedVars.st.put(info)

        if logic.games_byId[info.chat.id].players[logic.games_byId[
                info.chat.id].current_position].name == player and any(
                    info.text == logic.games_byId[info.chat.id].players[
                        logic.games_byId[
                            info.chat.id].current_position].cards[ind].name
                    for ind in range(
                        len(logic.games_byId[info.chat.id].players[
                            logic.games_byId[
                                info.chat.id].current_position].cards))):
            sharedVars.st.put(info)

        if logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].name == player and \
                logic.games_byId[info.chat.id].next_color is False:
            sharedVars.st.put(info)
