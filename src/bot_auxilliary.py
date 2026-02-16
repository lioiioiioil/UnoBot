import sharedVars
import unoBot
import logic
import telebot
from telebot import types
from threading import Thread

def start(info):
    '''Начальное приветствие.'''
    unoBot.safe_send_message(info.chat.id, 'Этот бот предназначен для проведения игры уно в телеграмме. Для запуска игры добавьте бота в свою группу, и напишите /start_game.')

def admin(info):
    unoBot.safe_send_message(info.chat.id, 'Создатели:\n@shout_0_0\n@rbedin25\n@n3tw4lk3r')

def stiker(info):
    '''Небольшая пасхалка.'''
    unoBot.safe_send_sticker(info.chat.id, 'CAACAgIAAxkBAAEBpnZlPXSscqnvN_rM-uZusGxvanFG2wACuCQAArgGAUiH8Vp5cuhbHDAE')

def win(info):
    '''он был умнее остальных'''
    logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].cards = []

def join(info):
    '''Присоединение игрока после начала игры.'''
    if info.chat.id in logic.games_byId and info.from_user.username not in logic.games_byId[info.chat.id].player_hasActed:
        unoBot.safe_send_message(info.chat.id, f'Игрок {info.from_user.username} добавлен')
        logic.games_byId[info.chat.id].add_player(info.from_user.username, info.from_user.id)

def help(info):
    '''Помощь с командами.'''
    msg = '/start_game - запускает игру \n /end_game - заканчивает игру \n выбор картоы нажатием на кнопку в сообщениях\n /admin - связь с админами \n /join - присоедениться к игре \n /play- начать игру'
    unoBot.safe_send_message(info.chat.id, msg)

def help_game(info):
    msg = 'Игра UNO предназначена для группы от 2 до 10 игроков. Каждый игрок получает по 7 карт, а одна карта остается в центре как “ведущая” карта. Все карты имеют номера от 1 до 9 и два специальных значения: “Реверс” и “+2”. Цель игры - быть первым, кто избавится от всех своих карт. \n Правила игры: \n1. Игроки ходят по часовой стрелке. \n2. Каждый игрок должен положить карту соответствующего цвета или значения, если возможно(чёрные карты можно положить по верх любой из карт, после этого игрок выбирает цвет, который будет главным после этой карты). \n3. Если игрок не может положить подходящую карту, он берет одну карту из колоды ,и если после этого он до сих пор не может сходить, то пропускает ход. \n4. При выпадении “Реверса”, все игроки должны поменять направление своего хода. \n5. Карта “+2” заставляет следующего игрока взять две карты.\n 6. Победителем становится последний игрок, без карт.\n 7. Остальные места распределяются по количеству баллов(баллы считаются в зависимости от оставшихся карт в руке)'
    unoBot.safe_send_message(info.chat.id, msg)

def end_game(info):
    '''Принудительное завершение игры.'''
    #Проверяет была ли запущенна игра
    if info.chat.id in logic.games_byId and logic.games_byId[info.chat.id].isRunning:
        if info.from_user.username in logic.games_byId[info.chat.id].player_hasActed:
            markup = telebot.types.ReplyKeyboardRemove()
            logic.games_byId[info.chat.id].isRunning = False
    else:
        markup = telebot.types.ReplyKeyboardRemove()
        unoBot.safe_send_message(info.chat.id, 'Игра не запущена(', reply_markup=markup)

def start_game(info):
    '''Запуск создания игры.'''

    if logic.isGameRunning(info.chat.id):
        unoBot.safe_send_message(info.chat.id, 'Не тупи, игра уже идёт.')
        return

    logic.games_byId[info.chat.id] = logic.game(info.chat.id)
    #print(info.chat.id)
    unoBot.safe_send_message(info.chat.id,'''Охаё, они чан) Создай свою игру\n''')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Начать игру")
    button2 = types.KeyboardButton("Присоединиться")
    keyboard.add(button2, button1)

    unoBot.safe_send_message(info.chat.id, 'Нажмите присоединиться, чтобы войти в игру. Нажмите начать игру, для запуска игры.', reply_markup=keyboard)

def stats(info):
    '''Показывает игроков в игре.'''
    try:
      msg = "Уважаемые игроки:\n"
      for player in logic.games_byId[info.chat.id].players:
          msg += str(player.name) + "\n"
      unoBot.safe_send_message(info.chat.id, msg)
    except Exception as e:
      unoBot.safe_send_message(info.chat.id, "Никто в этом чате не играет(")

def play(info):
    '''Запуск игры.'''
    markup = telebot.types.ReplyKeyboardRemove()
    #проверка на условия запуска игры
    if info.chat.id not in logic.games_byId or logic.games_byId[info.chat.id].isRunning or len(logic.games_byId[info.chat.id].players) == 0:
        unoBot.safe_send_message(info.chat.id, "Что-то пошло не так(")
        return
    unoBot.safe_send_message(info.chat.id, "Да начнётся игра!!!))", reply_markup=markup)
    logic.games_byId[info.chat.id].isRunning = True
    sharedVars.threadsByChatId[info.chat.id] = Thread(target=logic.games_byId[info.chat.id].game)
    sharedVars.threadsByChatId[info.chat.id].start()

def clear(info):
    '''Очистка полей кнопок.'''
    markup = telebot.types.ReplyKeyboardRemove()
    unoBot.safe_send_message(info.chat.id, "Очищаю кнопочки", reply_markup=markup)


def take_card_or_skip(info):
    player = info.from_user.username
    logic.games_byId[info.chat.id].player_hasActed[player] = True
    logic.games_byId[info.chat.id].player_lastMove[player] = -1

def put_card(info):
    player = info.from_user.username
    for ind in range(
            len(logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].cards)):
        if info.text == logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].cards[
            ind].name:
            logic.games_byId[info.chat.id].player_hasActed[player] = True
            logic.games_byId[info.chat.id].player_lastMove[player] = int(ind)
            break

def change_color(info):
    player = info.from_user.username
    logic.games_byId[info.chat.id].player_hasActed[player] = True
    if info.text == '🟩':
      logic.games_byId[info.chat.id].next_color = 'green'
    elif info.text == '🟨':
      logic.games_byId[info.chat.id].next_color = 'yellow'
    elif info.text == '🟦':
      logic.games_byId[info.chat.id].next_color = 'blue'
    elif info.text == '🟥':
      logic.games_byId[info.chat.id].next_color = 'red'

