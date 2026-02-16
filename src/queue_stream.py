import time
import logic
from queue import Queue
import bot_auxilliary

class stream:
    def __init__(self):
        self.stream = Queue()

    def put(self, item):
        self.stream.put(item)

    def run(self):
        #prev = False
        while True:
            if not self.stream.empty():
                time.sleep(1)
                info = self.stream.get()
                #while prev != False and info.text == prev.text and info.from_user.username == prev.from_user.username:
                #    info = self.stream.get()
                #prev = info
                player = info.from_user.username
                text = info.text
                if '/start_game' in text:
                    bot_auxilliary.start_game(info)
                elif '/start' in text:
                    bot_auxilliary.start(info)
                elif '/stats' in text:
                    bot_auxilliary.stats(info)
                elif '/stiker' in text:
                    bot_auxilliary.stiker(info)
                elif '/end_game' in text:
                    bot_auxilliary.end_game(info)
                elif '/admin' in text:
                    bot_auxilliary.admin(info)
                elif '/help_game' in text:
                    bot_auxilliary.help_game(info)
                elif '/help' in text:
                    bot_auxilliary.help(info)
                elif '/join' in text or 'Присоединиться' in text:
                    bot_auxilliary.join(info)
                elif '/play' in text or "Начать игру" in text:
                    bot_auxilliary.play(info)
                elif '/clear' in text:
                    bot_auxilliary.clear(info)
                elif info.chat.id in logic.games_byId and logic.games_byId[info.chat.id].isRunning and \
                        (info.text == "Взять карту" or info.text == "Пропуск хода") \
                        and logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].name == player \
                        and logic.games_byId[info.chat.id].next_color != False:
                    bot_auxilliary.take_card_or_skip(info)
                elif info.chat.id in logic.games_byId and logic.games_byId[info.chat.id].isRunning and \
                        logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].name == player \
                        and logic.games_byId[info.chat.id].next_color != False \
                        and any(info.text == logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].cards[ind].name \
                                for ind in range(len(logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].cards))):
                    bot_auxilliary.put_card(info)
                elif info.chat.id in logic.games_byId and logic.games_byId[info.chat.id].isRunning and \
                        logic.games_byId[info.chat.id].players[logic.games_byId[info.chat.id].current_position].name == player \
                        and logic.games_byId[info.chat.id].next_color == False:
                    bot_auxilliary.change_color(info)
