import tactics as ta
import random as ra
import config
import utils


class Mind:
    def __init__(self, max_round):
        self.max_round = max_round
        self.ai_list = [TacticAI(i) for i in range(len(ta.All_Tactic))]
        # self.ai_list = [TacticAI(12), TacticAI(10), TacticAI(10), TacticAI(11)]

        self.champion_data_file_name = "data/冠军统计.csv"
        self.runner_data_file_name = "data/亚军统计.csv"
        self.third_data_file_name = "data/季军统计.csv"
        self.fourth_data_file_name = "data/第四统计.csv"
        self.die_data_file_name = "data/死亡统计.csv"
        self.fire_data_file_name = "data/开火统计.csv"
        self.card_data_file_names = ["data/真牌数量_{}.csv".format(i) for i in range(6)]
        self.file_names = [self.champion_data_file_name,
                           self.runner_data_file_name,
                           self.third_data_file_name,
                           self.fourth_data_file_name,
                           self.die_data_file_name,
                           self.fire_data_file_name, *self.card_data_file_names]
        self.win_table_info = {}
        for i in range(6):
            self.win_table_info[(i, 0)] = [0 for _ in ta.All_Tactic]
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
        else:
            self.write_win_info_to_file()
        if IS_TEST:
            self.show_ai_info()
        self.close()

    def write(self, now_round, tactics_data):
        if not IS_TEST:
            self.write_win_count(tactics_data)  # 记录按手牌未出局的信息
        if now_round % 100 != 0:
            return
        for index, f in enumerate(self.files[:6]):
            f.write("第{}回合,".format(now_round) + self._get_csv_line(index, tactics_data) + "\n")

    def write_win_info_to_file(self):
        for index, f in enumerate(self.files[6:]):
            f.write(self.gen_win_table_info(index))

    def gen_win_table_info(self, index):
        keys = []
        for key in self.win_table_info.keys():
            if key[0] == index:
                keys.append(key)
        keys.sort(key=lambda k: k[1])
        m = 1
        while m < len(keys):
            c = 0
            check_key = keys[m - 1]
            key = keys[m]
            new_keys_count = 1
            while c < key[1] - (check_key[1] + 1):
                keys.insert(m, (key[0], key[1] - c - 1))
                new_keys_count += 1
                c += 1
            m += new_keys_count
        for i in range(len(keys)):
            if i == 0:
                continue
            key = keys[i]
            data = self.win_table_info.get(key, [0 for _ in ta.All_Tactic])
            for j, v in enumerate(data):
                if v == 0:
                    data[j] = self.win_table_info[keys[i - 1]][j]
                    self.win_table_info[key] = data
        info = []
        for key in keys:
            info.append(",".join(["回合数{}".format(key[1]), *[str(s) for s in self.win_table_info[key]]]))
        return "\n".join(info)

    def write_win_count(self, tactics_data):
        for i in range(len(ta.All_Tactic)):
            win_count = tactics_data[i][6]
            max_card_count = tactics_data[i][7]
            for index, j in enumerate(max_card_count):
                table = self.win_table_info.get((index, j), [0 for _ in ta.All_Tactic])
                table[i] = win_count[index]
                self.win_table_info[(index, j)] = table

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
            if self != card:
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
        self.turn_times = 0  # 决策次数，轮到该玩家的次数
        self.deny_times = 0  # 质疑次数
        self.now_has_real_card_count_max = 0  # 本轮次总共拥有的真牌数
        self.first_drop_deny_real_max = 0
        self.first_drop_deny_real_count = 0
        # 统计信息
        self.champion_count = 0
        self.runner_count = 0
        self.third_count = 0
        self.fourth_count = 0
        self.die_count = 0
        self.fire_count = 0
        self.real_card_win = [0, 0, 0, 0, 0, 0]  # 当只有i张真牌并且没有出局的次数
        self.real_card_count = [0, 0, 0, 0, 0, 0]  # 当只有i张真牌的次数

    # 检查是否只有假牌
    def is_all_fake(self):
        for card in self.cards:
            if card == self.game.key_card:
                return False
        return True

    # 检查是否只有真牌
    def is_all_real(self):
        for card in self.cards:
            if card != self.game.key_card:
                return False
        return True

    # 出指定数量的真牌或假牌
    def drop_cards(self, num, is_real):
        card_list = []
        num = min(3, num)
        index = 0
        while len(card_list) < num:
            if (is_real and (self.cards[index] == self.game.key_card)) or \
                    (not is_real and (self.cards[index] != self.game.key_card)):
                card_list.append(self.cards[index])
                self.cards.pop(index)
            else:
                index += 1
        self.game.drop(card_list, self)

    # 获取玩家每轮第一次出牌且被质疑后是真牌的概率
    def get_first_drop_deny_real(self):
        if self.first_drop_deny_real_max == 0:
            return 0
        return self.first_drop_deny_real_count / self.first_drop_deny_real_max

    def get_deny_rate(self):
        if self.turn_times == 0:
            return 0
        return self.deny_times / self.turn_times

    # 获取真牌的数量
    def get_real_card_num(self):
        return self.cards.count(self.game.key_card)

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
            self.fire_count, self.real_card_win, self.real_card_count

    def reload(self, player_index):
        self.player_index = player_index
        self.bullet_index = ra.randint(0, 5)
        self.is_die = False
        self.turn_times = 0  # 新局开始时次数清空，作为其他玩家的陌生人开始游戏
        self.deny_times = 0

    def get_cards(self, *cards: Card):
        if self.is_die:
            return False
        self.cards = list(cards)
        self.real_card_count[self.get_real_card_num()] += 1
        self.now_has_real_card_count_max = self.get_real_card_num()
        self.switch = True
        return True

    def add_real_card_count(self):
        if self.is_die:
            return
        self.real_card_win[self.now_has_real_card_count_max] += 1

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
            return False
        if self.bullet_index < 0:
            return False
        if self.game.has_card_player_count == 1:
            self.game.fire_end_player(self)
            return False
        self.turn_times += 1
        if self.tactic not in ta.No_Assist_Tactic:
            if self._tactic_all_real():
                return True
        self.tactic(self, self.game, is_first)
        return True

    def if_has_cards(self):
        return not self.is_die and len(self.cards) > 0

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
        self.epoch = 0
        self.card_last = []  # 上家出的牌
        self.card_last_from = None  # 谁出的牌
        self.now_ai_index = 0
        self.has_card_player_count = 4  # 还有多少玩家有手牌
        self.game_round = game_round
        self.is_finish = False

    # 获取上个玩家每轮第一次出牌且被质疑后是真牌的概率
    def get_pre_ai_first_drop_deny_real(self, ai):
        index = (ai.player_index - 1) % len(self.ai_list)
        while index != ai.player_index:
            if self.ai_list[index].if_has_cards():
                return self.ai_list[index].get_first_drop_deny_real()
            index = (index - 1) % len(self.ai_list)
        return 0

    # 获取下家质疑概率
    def get_next_ai_deny_rate(self, ai):
        index = (ai.player_index + 1) % len(self.ai_list)
        while index != ai.player_index:
            if self.ai_list[index].if_has_cards():
                return self.ai_list[index].get_deny_rate()
            index = (index + 1) % len(self.ai_list)
        return 0

    # 场上还有手牌的玩家
    def get_ai_count(self):
        return self.has_card_player_count

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

    def add_ais_real_card_win(self, not_included_ai_index):
        for ai in self.ai_list:
            if ai.player_index != not_included_ai_index:
                ai.add_real_card_count()

    def deny(self, deny_ai: TacticAI):
        if self.key_card is None:
            log("系统未抽排！！！")
            return
        log("{}玩家质疑了".format(deny_ai.player_index))
        if self.card_last_from.turn_times == 1:
            self.card_last_from.first_drop_deny_real_max += 1
        deny_ai.deny_times += 1
        if self.key_card.check(self.card_last):
            deny_ai.fire()
            self.add_ais_real_card_win(deny_ai.player_index)
            if self.card_last_from.turn_times == 1:
                self.card_last_from.first_drop_deny_real_count += 1
        else:
            self.card_last_from.fire()
            self.add_ais_real_card_win(self.card_last_from.player_index)
        self.is_finish = True

    def fire_end_player(self, ai: TacticAI):
        """只剩最后一个玩家时自己开枪"""
        ai.fire()
        self.add_ais_real_card_win(ai.player_index)
        self.is_finish = True

    def read_data(self):
        dirs = {}
        for ai in self.ai_list:
            if ai.is_virtual:
                continue
            dirs[ai.tactic_index] = ai.read_data()
        return dirs

    def run(self):
        self.epoch += 1
        self.key_card = Card.choice()
        self.card_last = []
        self.card_last_from = None
        self.is_finish = False
        self.has_card_player_count = 0
        log("当前卡牌：", self.key_card.card_type, "*代表假牌")
        cards = Card.cards()
        for index, ai in enumerate(self.ai_list):
            if ai.get_cards(*cards[5 * index:5 * (index + 1)]):
                log("{}手牌：{}".format(ai.player_index, self.key_card.show_cards(ai.cards)))
                self.has_card_player_count += 1
        is_first = True
        while not self.is_finish:
            if self.ai_list[self.now_ai_index].discard(is_first):
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


log = utils.log
TEST_ONE_TIME = config.TEST_ONE_TIME  # 仅测试到第一次打牌结束（有人开枪或者只剩一人未出完牌）
IS_TEST = config.IS_TEST  # 当该值为False时会记录数据到文件，请注意

mind = Mind(1000000)
mind.run()
utils.log_close()
