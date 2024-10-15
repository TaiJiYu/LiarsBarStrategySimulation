import random as ra


def tactic_0(ai, game, is_first):
    """
    策略一
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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


def tactic_1(ai, game, is_first):
    """
        策略二：
        :param ai:
        :param game:
        :param is_first:
        :return:
        """
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


def tactic_2(ai, game, is_first):
    """
    策略三：先出真的，每次出一张，没有真的再质疑先出真的，每次出一张，没有真的再质疑
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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


def tactic_3(ai, game, is_first):
    """
    策略四：尽量先出完假的，再出真的
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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


def tactic_4(ai, game, is_first):
    """
    策略五：尽量先出完真的，再出假的
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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


def tactic_5(ai, game, is_first):
    """
    策略六：每次出一张，真假穿插
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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


def tactic_6(ai, game, is_first):
    """
    策略七：上家出3张必质疑，否则按照策略四
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
    if len(game.card_last) == 3:
        game.deny(ai)
        return
    tactic_3(ai, game, is_first)


def tactic_7(ai, game, is_first):
    """
    策略八：上家出3张必质疑，否则按照策略五
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
    if len(game.card_last) == 3:
        game.deny(ai)
        return
    tactic_4(ai, game, is_first)


def tactic_8(ai, game, is_first):
    """
    策略九：尽可能出完真牌，没有真的必质疑
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
    card_list = []
    index = 0
    while len(ai.cards) > 0 and len(card_list) < 3 and index < len(ai.cards):
        if ai.cards[index] == game.key_card:
            card_list.append(ai.cards[index])
            ai.cards.pop(index)
        else:
            index += 1
    if len(card_list) == 0:
        game.deny(ai)
    else:
        game.drop(card_list, ai)


def tactic_9(ai, game, is_first):
    """
    策略十：第一次必质疑，之后按照策略九
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
    if len(game.card_last) != 0 and ai.switch:
        ai.switch = False
        game.deny(ai)
        return
    tactic_8(ai, game, is_first)


def tactic_10(ai, game, is_first):
    """
    策略十一：只质疑，首发出牌按照策略五
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
    if is_first:
        tactic_4(ai, game, is_first)
    else:
        game.deny(ai)


def tactic_11(ai, game, is_first):
    """
    策略十二：先每次一张出假的，再尽快出真的
    :param ai:
    :param game:
    :param is_first:
    :return:
    """
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
    # tactic_11
]
