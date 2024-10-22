import tactics as ta
import random as ra


class Mind:
    def __init__(self, max_round):
        self.max_round = max_round
        self.ai_list = [TacticAI(i) for i in range(len(ta.All_Tactic))]
        self.champion_data_file_name = "data/冠军统计.csv"
        self.runner_data_file_name = "data/亚军统计.csv"
        self.third_data_file_name = "data/季军统计.csv"
        self.fourth_data_file_name = "data/第四统计.csv"
        self.die_data_file_name = "data/死亡统计.csv"
        self.fire_data_file_name = "data/开火统计.csv"
        self.file_names = [self.champion_data_file_name,
                           self.runner_data_file_name,
                           self.third_data_file_name,
                           self.fourth_data_file_name,
                           self.die_data_file_name,
                           self.fire_data_file_name]
        self.files = []
        if not IS_TEST:
            self.init_file()

    def init_file(self):
        info = []
        for i in range(len(ta.All_Tactic)):
            info.append("策略{}".format(i + 1))
        title = ",{}".format(",".join(info))
        for name in self.file_names:
            with open(name, "w") as f:
                f.write(title + "\n")
                f.close()
                self.files.append(open(name, "a"))

    def close(self):
        for f in self.files:
            f.close()

    def run(self):
        for i in range(self.max_round):
            ra.shuffle(self.ai_list)
            tactics_data = {}
            r = 0
            for j in range(len(self.ai_list) // 4):
                r = (j + 1) * 4
                game = Game(i + 1, *self.ai_list[j * 4:r])
                game.run()
                tactics_data.update(game.read_data())
            if r != len(self.ai_list):
                game = Game(i + 1, *self.ai_list[r:])
                game.run()
                tactics_data.update(game.read_data())
            self.write(i + 1, tactics_data)
            print("第{}回合结束".format(i + 1))
        if IS_TEST:
            self.show_ai_info()
        self.close()

    def write(self, now_round, tactics_data):
        for index, f in enumerate(self.files):
            f.write("第{}回合,".format(now_round) + self._get_csv_line(index, tactics_data) + "\n")

    @staticmethod
    def _get_csv_line(index, tactics_data: {}):
        data = []
        for i in range(len(ta.All_Tactic)):
            data.append(str(tactics_data[i][index]))
        return ",".join(data)

    def show_ai_info(self):
        self.ai_list.sort(key=lambda i: i.champion_count, reverse=True)
        for ai in self.ai_list:
            print(ai.show())


class Card:
    Card_K = "K"
    Card_Q = "Q"
    Card_A = "A"
    Card_JOKER = "J"

    def __init__(self, card_type):
        self.card_type = card_type

    @staticmethod
    def choice():
        return ra.choice([Card(Card.Card_K), Card(Card.Card_A), Card(Card.Card_Q)])

    @staticmethod
    def cards():
        card_list = [Card(Card.Card_K) for _ in range(6)] + \
                    [Card(Card.Card_A) for _ in range(6)] + \
                    [Card(Card.Card_Q) for _ in range(6)] + \
                    [Card(Card.Card_JOKER) for _ in range(2)]
        ra.shuffle(card_list)
        return card_list

    def check(self, card_list):
        for card in card_list:
            if self.card_type != card.card_type:
                return False
        return True

    def show_cards(self, cards):
        info = []
        for card in cards:
            if self == card:
                info.append(card.card_type)
            else:
                info.append("*{}".format(card.card_type))
        return ",".join(info)

    def __eq__(self, other):
        if other.card_type == Card.Card_JOKER:
            return True
        if self.card_type == Card.Card_JOKER:
            return True
        return other.card_type == self.card_type


class TacticAI:
    def __init__(self, tactic_index=0, is_virtual=False):
        self.game = None
        self.player_index = 0
        self.tactic_index = tactic_index
        self.tactic = ta.All_Tactic[tactic_index]
        self.cards = []
        self.bullet_index = 0
        self.is_die = False
        self.is_virtual = is_virtual
        # 策略辅助信息
        self.switch = True
        # 统计信息
        self.champion_count = 0
        self.runner_count = 0
        self.third_count = 0
        self.fourth_count = 0
        self.die_count = 0
        self.fire_count = 0

    def show(self):
        return "策略:{} 第一:{} 第二:{} 第三:{} 第四:{} 死亡:{} 开枪:{}". \
            format(self.tactic_index + 1, self.champion_count, self.runner_count,
                   self.third_count, self.fourth_count, self.die_count, self.fire_count)

    def read_data(self):
        return self.champion_count, \
            self.runner_count, \
            self.third_count, \
            self.fourth_count, \
            self.die_count, \
            self.fire_count

    def reload(self, player_index):
        self.player_index = player_index
        self.bullet_index = ra.randint(0, 5)
        self.is_die = False

    def get_cards(self, *cards: Card):
        if self.is_die:
            return False
        self.cards = list(cards)
        self.switch = True
        return True

    # 全是真牌直接出
    def _tactic_all_real(self):
        for card in self.cards:
            if card != self.game.key_card:
                return False
        card_list = []
        while len(card_list) < 3 and len(self.cards) > 0:
            card_list.append(self.cards[0])
            self.cards.pop(0)
        self.game.drop(card_list, self)
        return True

    def discard(self, is_first):
        if len(self.cards) == 0:
            return
        if self.bullet_index < 0:
            return
        if self.game.has_card_player_count == 1:
            self.game.fire_end_player(self)
            return
        if self._tactic_all_real():
            return
        self.tactic(self, self.game, is_first)

    def fire(self):
        log("{}玩家开枪了".format(self.player_index))
        self.fire_count += 1
        self.bullet_index -= 1
        if self.bullet_index < 0:
            rank = self.game.get_rank()
            if rank == 2:
                self.runner_count += 1
            elif rank == 3:
                self.third_count += 1
            elif rank == 4:
                self.fourth_count += 1
            self.die_count += 1
            self.is_die = True


class Game:
    def __init__(self, game_round=1, *ai_list: TacticAI):
        self.ai_list = list(ai_list)
        if len(self.ai_list) < 4:
            abs_num = 4 - len(self.ai_list)
            self.ai_list += [TacticAI(ra.randint(0, len(ta.All_Tactic) - 1), is_virtual=True) for _ in range(abs_num)]
            log("增加{}个虚拟ai，当前ai个数：{}".format(abs_num, len(self.ai_list)))
        for index, ai in enumerate(self.ai_list):
            ai.game = self
            ai.reload(index)
        self.key_card = None
        self.card_last = []  # 上家出的牌
        self.card_last_from = None  # 谁出的牌
        self.now_ai_index = 0
        self.has_card_player_count = 4  # 还有多少玩家有手牌
        self.game_round = game_round
        self.is_finish = False

    def drop(self, card_list, drop_ai: TacticAI):
        self.card_last = card_list
        self.card_last_from = drop_ai
        if len(drop_ai.cards) == 0:
            self.has_card_player_count -= 1

        log("{}出了牌：{}".format(drop_ai.player_index, self.key_card.show_cards(card_list)))

    def get_rank(self):
        count = 0
        for ai in self.ai_list:
            if not ai.is_die:
                count += 1
        return count

    def deny(self, deny_ai: TacticAI):
        if self.key_card is None:
            log("系统未抽排！！！")
            return
        log("{}玩家质疑了".format(deny_ai.player_index))
        if self.key_card.check(self.card_last):
            deny_ai.fire()
        else:
            if self.card_last_from is None:
                print("出错了，无法质疑，上家不存在")
            else:
                self.card_last_from.fire()
        self.is_finish = True

    def fire_end_player(self, ai: TacticAI):
        """只剩最后一个玩家时自己开枪"""
        ai.fire()
        self.is_finish = True

    def read_data(self):
        dirs = {}
        for ai in self.ai_list:
            if ai.is_virtual:
                continue
            dirs[ai.tactic_index] = ai.read_data()
        return dirs

    def run(self):
        self.key_card = Card.choice()
        self.card_last = []
        self.card_last_from = None
        self.is_finish = False
        self.has_card_player_count = 0
        log("当前卡牌：", self.key_card.card_type)
        cards = Card.cards()
        for index, ai in enumerate(self.ai_list):
            if ai.get_cards(*cards[5 * index:5 * (index + 1)]):
                log("{}手牌：{}".format(ai.player_index, self.key_card.show_cards(ai.cards)))
                self.has_card_player_count += 1
        is_first = True
        while not self.is_finish:
            self.ai_list[self.now_ai_index].discard(is_first)
            is_first = False
            self.now_ai_index = (self.now_ai_index + 1) % len(self.ai_list)
        if TEST_ONE_TIME:
            return
        count = 0
        for ai in self.ai_list:
            if not ai.is_die:
                count += 1
        if count > 1:
            self.run()
        else:
            for ai in self.ai_list:
                if not ai.is_die:
                    ai.champion_count += 1
                    log("第{}回合玩家{}获胜,策略{}".format(self.game_round, ai.player_index, ai.tactic_index + 1))
                    return


def log(*info):
    if IS_TEST:
        print(*info)


TEST_ONE_TIME = False  # 仅测试到第一次打牌结束（有人开枪或者只剩一人未出完牌）
IS_TEST = True  # 当该值为False时会记录数据到文件，请注意

mind = Mind(1)
mind.run()
