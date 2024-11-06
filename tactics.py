import random as ra
import utils


def provider(name):
    def _(f):
        def _w(*args, **kwargs):
            f(*args, **kwargs)
            utils.log("\b  ---@{}".format(name))

        return _w

    return _


# 策略一：随机出，随机质疑,轮到你时，有一半几率决定出牌，50%几率决定质疑，首发出牌或决定出牌则随机
# 抽取
def tactic_0(ai, game, is_first):
    k = ra.random()
    if is_first or k < 0.5:
        count = ra.randint(1, 3)
        card_list = []
        while len(ai.cards) > 0 and count > 0:
            card_list.append(ai.cards[0])
            ai.cards.pop(0)
            count -= 1
        game.drop(card_list, ai)
    else:
        game.deny(ai)


# 策略二：先出随机张数的真牌，没有真牌就质疑
# 	如果首发出牌没有真牌，则出随机张数假牌
def tactic_1(ai, game, is_first):
    count = ra.randint(1, 3)
    card_list = []
    check_index = 0
    while count > 0 and len(ai.cards) > 0 and check_index < len(ai.cards):
        if ai.cards[check_index] == game.key_card:
            card_list.append(ai.cards[check_index])
            ai.cards.pop(check_index)
            count -= 1
        else:
            check_index += 1
    if len(card_list) == 0:
        if is_first:
            while count > 0 and len(ai.cards) > 0:
                card_list.append(ai.cards[0])
                ai.cards.pop(0)
                count -= 1
            game.drop(card_list, ai)
        else:
            game.deny(ai)
    else:
        game.drop(card_list, ai)


# 策略三：先出真牌，每次出一张，没有真牌就质疑
# 如果首发出牌没有真牌，则出第一张假牌
def tactic_2(ai, game, is_first):
    card_list = []
    for index, card in enumerate(ai.cards):
        if card == game.key_card:
            card_list.append(card)
            ai.cards.pop(index)
            break
    else:
        if is_first:
            card_list.append(ai.cards[0])
            ai.cards.pop(0)
        else:
            game.deny(ai)
            return
    game.drop(card_list, ai)


# 策略四：尽快先出完假牌，再尽快出真牌
# 	尽快：有大于3张牌出3张，只有两张出两张，只有一张出一张
def tactic_3(ai, game, is_first):
    card_list = []
    index = 0
    while len(ai.cards) > 0 and len(card_list) < 3 and index < len(ai.cards):
        if ai.cards[index] != game.key_card:
            card_list.append(ai.cards[index])
            ai.cards.pop(index)
        else:
            index += 1
    if len(card_list) == 0:
        while len(card_list) < 3 and len(ai.cards) > 0:
            card_list.append(ai.cards[0])
            ai.cards.pop(0)
    game.drop(card_list, ai)


# 策略五：尽快先出完真牌，再尽快出假牌
# 尽快：有大于3张牌出3张，只有两张出两张，只有一张出一张
def tactic_4(ai, game, is_first):
    card_list = []
    index = 0
    while len(ai.cards) > 0 and len(card_list) < 3 and index < len(ai.cards):
        if ai.cards[index] == game.key_card:
            card_list.append(ai.cards[index])
            ai.cards.pop(index)
        else:
            index += 1
    if len(card_list) == 0:
        while len(card_list) < 3 and len(ai.cards) > 0:
            card_list.append(ai.cards[0])
            ai.cards.pop(0)
    game.drop(card_list, ai)


# 策略六：每次只出一张，真假穿插
def tactic_5(ai, game, is_first):
    card_list = []
    for index, card in enumerate(ai.cards):
        if (ai.switch and (card == game.key_card)) or ((not ai.switch) and (card != game.key_card)):
            card_list.append(card)
            ai.cards.pop(index)
            break
    ai.switch = not ai.switch
    if len(card_list) == 0:
        card_list.append(ai.cards[0])
        ai.cards.pop(0)
    game.drop(card_list, ai)


# 策略七：上家出3张牌必质疑，否则按照策略四
# 	策略四：尽快先出完假牌，再尽快出真牌
def tactic_6(ai, game, is_first):
    if len(game.card_last) == 3:
        game.deny(ai)
        return
    tactic_3(ai, game, is_first)


# 策略八：上家出3张牌必质疑，否则按照策略五
# 策略五：尽快先出完真牌，再尽快出假牌
def tactic_7(ai, game, is_first):
    if len(game.card_last) == 3:
        game.deny(ai)
        return
    tactic_4(ai, game, is_first)


# 策略九：尽快先出真牌，没有真牌必质疑
# 尽快：有大于3张牌出3张，只有两张出两张，只有一张出一张
def tactic_8(ai, game, is_first):
    real_num = ai.get_real_card_num()
    if real_num != 0:
        ai.drop_cards(real_num, True)
    else:
        if is_first:
            ai.drop_cards(len(ai.cards) - real_num, False)
        else:
            game.deny(ai)


# 策略十：第一次出牌必质疑，之后按照策略九
# 	策略九：尽快先出真牌，没有真牌必质疑
def tactic_9(ai, game, is_first):
    if len(game.card_last) != 0 and ai.switch:
        ai.switch = False
        game.deny(ai)
        return
    tactic_8(ai, game, is_first)


# 策略十一：只质疑
def tactic_10(ai, game, is_first):
    if is_first:
        tactic_4(ai, game, is_first)
    else:
        game.deny(ai)


# 策略十二：每次只出一张出假牌，没有假牌，再尽快出真牌
# 尽快：有大于3张牌出3张，只有两张出两张，只有一张出一张
def tactic_11(ai, game, is_first):
    card_list = []
    index = 0
    while len(card_list) < 3 and len(ai.cards) > 0 and index < len(ai.cards):
        if ai.cards[index] != game.key_card:
            card_list.append(ai.cards[index])
            ai.cards.pop(index)
            break
        index += 1
    else:
        while len(card_list) < 3 and len(ai.cards) > 0:
            card_list.append(ai.cards[0])
            ai.cards.pop(0)
    game.drop(card_list, ai)


# 有1/n的概率质疑，有1-1/n的概率出假牌，n位当前人数
@provider("莫之随")
def tactic_12(ai, game, is_first):
    if ai.is_all_real():
        ai.drop_cards(min(ai.get_real_card_num(), 2), True)
        return
    if game.get_ai_count() == 2 and ai.is_all_fake():
        if is_first:
            ai.drop_cards(1, False)
        else:
            game.deny(ai)
        return
    a = game.get_pre_ai_first_drop_deny_real(ai)
    b = game.get_next_ai_deny_rate(ai)
    n = game.get_ai_count()
    real_card_num = ai.get_real_card_num()
    fake_card_num = len(ai.cards) - real_card_num
    if not is_first:
        if game.epoch == 1:
            if a < 1 / n or (a == 1 / n and ra.random() < 1 / n):
                game.deny(ai)
                return
        else:
            if ra.random() < 1 / n:
                game.deny(ai)
                return
    if b < 1 / n:
        if ai.is_all_real():
            ai.drop_cards(min(ai.get_real_card_num(), 2), True)
            return
        ai.drop_cards(min(2, fake_card_num), False)
        return
    else:
        if real_card_num == 0:
            ai.drop_cards(min(2, fake_card_num), False)
        else:
            ai.drop_cards(1, True)


# 根据GTO策略而来，出真牌收益R=K*min(3,real_num),出假牌收益F=(1-K)*min(3,fake_num),质疑收益:D=3-R-F
# 按收益最高的方式走
@provider("需要白开")
def tactic_13(ai, game, is_first):
    k = game.get_next_ai_deny_rate(ai)
    real_num = ai.get_real_card_num()
    fake_num = len(ai.cards) - real_num
    r = k * min(3, real_num)
    f = (1 - k) * min(3, fake_num)
    d = 3 - r - f
    if is_first:
        if r > f and real_num > 0:
            ai.drop_cards(real_num, True)
        else:
            ai.drop_cards(fake_num, False)
    else:
        max_ex = max(r, f, d)
        if max_ex == d:
            game.deny(ai)
        elif max_ex == r and real_num > 0:
            ai.drop_cards(real_num, True)
        else:
            ai.drop_cards(fake_num, False)


# 两轮打完，第一回合先出2张牌，尽可能是真牌，第二回合出剩下的3张牌
@provider("我又挺行了")
def tactic_14(ai, game, is_first):
    if len(ai.cards) <= 3:
        card_list = ai.cards.copy()
        ai.cards.clear()
        game.drop(card_list, ai)
    else:
        real_num = ai.get_real_card_num()
        if real_num >= 2:
            ai.drop_cards(2, True)
        else:
            card_list = ai.cards[:2]
            ai.cards = ai.cards[2:]
            game.drop(card_list, ai)


# 随机混合各种策略
@provider("只是顆洋蔥")
def tactic_15(ai, game, is_first):
    tactics = All_Tactic.copy()
    tactics.remove(tactic_15)
    ra.choice(tactics)(ai, game, is_first)


All_Tactic = [
    tactic_0,
    tactic_1,
    tactic_2,
    tactic_3,
    tactic_4,
    tactic_5,
    tactic_6,
    tactic_7,
    tactic_8,
    tactic_9,
    tactic_10,
    tactic_11,
    tactic_12,
    tactic_13,
    tactic_14,
    tactic_15
]

No_Assist_Tactic = [
    tactic_12
]
