import numpy as np
import unoBot
import telebot
from telebot import types

class card:
    def __init__(self, num, col, step, count_cards, name_of_card, stiker_id, point):
        self.number = num
        self.color = col
        if step[:step.find(' ')] == 'forward':
            self.change_of_step = int(step[step.find(' ') + 1:])
        elif step[:step.find(' ')] == 'back':
            self.change_of_step = - int(step[step.find(' ') + 1:])
        elif step[:step.find(' ')] == 'through':
            self.change_of_step = int(step[step.find(' ') + 1:]) + 1
        else:
            self.change_of_step = int(step)
        self.cards_to_next_player = int(count_cards[1:])
        self.name = name_of_card
        self.stiker = stiker_id
        self.points = point

    def copy(self):
        return card(self.number, self.color, str(self.change_of_step), '+' + str(self.cards_to_next_player), self.name, self.stiker, self.points)


class player:
    def __init__(self, st, idd):
        self.name = st
        self.cards = []
        self.id = idd


class game:
    def __init__(self, tgId):
        self.players = []
        self.player_hasActed = {}
        self.player_lastMove = {}
        self.deck_of_cards = []
        self.top_of_deck = None
        self.current_position = 0
        self.next_color = None
        self.step = None
        self.isRunning = False
        self.chatId = tgId
        self.cards = []

        file = open("UNO cards.txt", 'r')
        while True:
            mas = file.readline().strip()
            if not mas:
                break
            mas = mas.split('~')
            p = mas[4].split()
            s = ''
            for j in range(len(p)):
                if p[j][0] == '!':
                    s += chr(int(p[j][1:])) + ' '
                else:
                    s += p[j] + ' '
            s = s[:-1]
            #print(*mas)
            self.cards.append(card(mas[0], mas[1], mas[2], mas[3], s, mas[5], int(mas[6])))
        file.close()
        self.index_in_cards = [i for i in range(len(self.cards))]

    def clear_fields(self):
        self.players = []
        self.player_hasActed = {}
        self.player_lastMove = {}
        self.deck_of_cards = []
        self.current_position = 0
        self.game_is_running = False
        self.next_color = False

    def new_deck(self):
        self.index_in_cards = np.random.permutation(self.index_in_cards)
        self.deck_of_cards = []
        for i in range(len(self.index_in_cards)):
            self.deck_of_cards.append(self.cards[self.index_in_cards[i]])

    def take_top_card(self):
        if len(self.deck_of_cards) == 0:
            self.new_deck()
        ans = self.deck_of_cards[0].copy()
        self.deck_of_cards = self.deck_of_cards[1:]
        return ans

    def add_player(self, name, iid):
        self.players.append(player(name, iid))
        self.player_hasActed[name] = False
        for j in range(6):
            self.players[len(self.players) - 1].cards.append(self.take_top_card())

    def can_put_card(self, ind):
        if (self.top_of_deck.color == 'universal') \
            or (self.players[self.current_position].cards[ind].number == self.top_of_deck.number \
            or self.players[self.current_position].cards[ind].color == self.top_of_deck.color) \
            or (self.players[self.current_position].cards[ind].number == 'universal' \
                and self.players[self.current_position].cards[ind].color == 'universal'):
            return True
        return False

    def put_card(self, ind):
        self.top_of_deck = self.players[self.current_position].cards[ind].copy()
        self.players[self.current_position].cards = self.players[self.current_position].cards[:ind] + self.players[self.current_position].cards[ind + 1:]
        for i in range(self.top_of_deck.cards_to_next_player):
            self.players[(len(self.players) + self.current_position + self.step) % len(self.players)].cards.append(self.take_top_card())

        if self.top_of_deck.number == 'universal' and self.top_of_deck.color == 'universal':
            buttons = [types.KeyboardButton("🟦"), types.KeyboardButton("🟨"), types.KeyboardButton("🟥"), types.KeyboardButton("🟩")]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, selective=True)
            keyboard.add(*buttons)
            unoBot.safe_send_message(self.chatId, '@' + self.players[self.current_position].name + ' выбери будущий цвет', reply_markup=keyboard)
            self.next_color = False
            self.player_hasActed[self.players[self.current_position].name] = False
            while self.isRunning and self.player_hasActed[self.players[self.current_position].name] is False:
                pass
            self.player_hasActed[self.players[self.current_position].name] = False
            self.top_of_deck.color = self.next_color

        if self.top_of_deck.change_of_step == 1 or self.top_of_deck.change_of_step == -1:
            self.step *= self.top_of_deck.change_of_step
            self.current_position = (len(self.players) + self.current_position + self.step) % len(self.players)
        else:
            self.current_position = (len(self.players) + self.current_position + self.step * self.top_of_deck.change_of_step) % len(self.players)

    def game(self):
        self.current_position = 0
        self.step = 1
        self.top_of_deck = self.take_top_card()

        while self.isRunning:
            markup = telebot.types.ReplyKeyboardRemove()
            unoBot.safe_send_message(self.chatId, 'Верхняя карта: ', reply_markup=markup)
            unoBot.safe_send_stiker(self.chatId, self.top_of_deck.stiker)
            if (self.top_of_deck.number == 'universal'):
                if self.top_of_deck.color == 'green':
                    unoBot.safe_send_message(self.chatId, 'Цвет: ' + '🟩')
                elif self.top_of_deck.color == 'yellow':
                    unoBot.safe_send_message(self.chatId, 'Цвет: ' + '🟨')
                elif self.top_of_deck.color == 'blue':
                    unoBot.safe_send_message(self.chatId, 'Цвет: ' + '🟦')
                elif self.top_of_deck.color == 'red':
                    unoBot.safe_send_message(self.chatId, 'Цвет: ' + '🟥')
            buttons = [types.KeyboardButton("Взять карту")]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, selective=True)
            for i in range(len(self.players[self.current_position].cards)):
                msg = self.players[self.current_position].cards[i].name
                buttons.append(types.KeyboardButton(msg))
            keyboard.add(*buttons)
            #time.sleep(1)
            unoBot.safe_send_message(self.chatId, '@' + self.players[self.current_position].name +' выбери номер карты, которую кинешь или возьми из колоды', reply_markup=keyboard)

            card_was_taken = False
            while True:
                while self.isRunning and self.player_hasActed[self.players[self.current_position].name] is False:
                    pass
                self.player_hasActed[self.players[self.current_position].name] = False
                if self.isRunning is False:
                    break
                num_in_players_cards = self.player_lastMove[self.players[self.current_position].name]
                if num_in_players_cards == -1:
                    if card_was_taken is False:
                        card_was_taken = True
                        self.players[self.current_position].cards.append(self.take_top_card())
                        num_in_players_cards = len(self.players[self.current_position].cards) - 1
                        if all( (not self.can_put_card(i)) for i in range(len(self.players[self.current_position].cards))):
                            buttons = [unoBot.types.KeyboardButton("Пропуск хода")]
                        else:
                            buttons = []
                        keyboard = unoBot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4,  selective=True)
                        for i in range(len(self.players[self.current_position].cards)):
                            msgg = self.players[self.current_position].cards[i].name
                            buttons.append(unoBot.types.KeyboardButton(msgg))
                        keyboard.add(*buttons)
                        unoBot.safe_send_message(self.chatId,
                                                '@' + self.players[self.current_position].name +" карта добавлена",
                                                reply_markup=keyboard)
                    else:
                        if all( (not self.can_put_card(i)) for i in range(len(self.players[self.current_position].cards))):
                            unoBot.safe_send_message(self.chatId, 'Пропускаешь ход, уви')
                            self.current_position = (len(self.players) + self.current_position + self.step) % len(self.players)
                            break
                        else:
                            unoBot.safe_send_message(self.chatId, 'Хватит брать карты из колоды!!!')
                else:
                    if self.can_put_card(num_in_players_cards):
                        self.put_card(num_in_players_cards)
                        break
                    else:
                        unoBot.safe_send_message(self.chatId, 'Такой карты нет(')

            if any(len(self.players[i].cards) == 0 for i in range(len(self.players))):
                pobed = 0
                for i in range(len(self.players)):
                    if len(self.players[i].cards) == 0:
                        pobed = i
                        unoBot.safe_send_message(self.chatId,f'ПОЗДРАВЛЯЕМ С ПОБЕДОЙ @{self.players[i].name}')
                        break
                strr = 'Остальные места по количеству штрафных баллов:\n'
                arr = []
                for i in range(len(self.players)):
                    if i != pobed:
                        sum = 0
                        for j in self.players[i].cards:
                           sum += j.points
                        arr.append((sum, self.players[i].name))
                arr.sort()
                for i in range(len(arr)):
                    summ, name = arr[i]
                    strr += f'{i+2} место @{name}  - {summ}б.\n'
                unoBot.safe_send_message(self.chatId, strr)
                self.isRunning = False

        markup = telebot.types.ReplyKeyboardRemove()
        unoBot.safe_send_message(self.chatId,
                                'Игра закончилась ну блииииин(((09((09(((',
                                reply_markup=markup)
        self.clear_fields()


def isGameRunning(gameId):
    global games_byId
    '''Активна ли игра с данным id.'''
    if gameId in games_byId:
        return games_byId[gameId].isRunning
    return False


# список всех активных игр
# ключ - id чата в tg, значение - экземпляр класса game
games_byId = {}
