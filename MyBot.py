"""
This is an example for a bot.
"""
from penguin_game import *
from helper import *
from attack import *
from neutrals import *
from rearFront import *


def build_negative_list(game, positive_icebergs, myIce):

    negative_icebergs = []
    useless_icebergs = []
    
    # check which of my icebergs needs help
    for my_iceberg in game.get_my_icebergs():
        if my_iceberg not in [ice.iceberg for ice in positive_icebergs]:
            amount, turn, status = final_penguins_num2(game, my_iceberg)
            if amount < 0:
                negative_icebergs.append(myIce(my_iceberg, amount * -1, turn, status))
            else:
                useless_icebergs.append(myIce(my_iceberg, amount, -1, status))
                
    # check which of the enemy icebergs will still be enemy consider the groups on the board
    for ice in game.get_enemy_icebergs():
        amount, turn, status = final_penguins_num2(game, ice)
        if amount < 0:
            negative_icebergs.append(myIce(ice, amount * -1, turn, status))
        else:
            enemy_icebergs = sorted(game.get_enemy_icebergs(), key=lambda x: x.get_turns_till_arrival(ice))
            for enemy_ice in enemy_icebergs:
                if enemy_ice != ice:
                    attack = amount + ice.penguins_per_turn * calc_real_dis(enemy_ice, ice) - enemy_ice.penguin_amount
                    if attack < 0:
                        negative_icebergs.append(myIce(ice, (attack * -1), 300))
                        break

    neutral_icebergs = []
    # get neutral that there are enemy in the way to them
    for ice in game.get_neutral_icebergs():
        amount, neutral = final_penguins_num_for_neutral(game, ice)
        if not neutral and amount < 0:
            negative_icebergs.append(myIce(ice, amount * -1))
        elif neutral:
            neutral_icebergs.append(ice)
            
    return negative_icebergs, useless_icebergs, neutral_icebergs
 
 
def predict_attack(game, ice, min_front, front):

    if ice.iceberg in min_front and len(min_front) < len(front):
        return ice.peng_amount
    max_attack = 0
    for enemy_ice in game.get_enemy_icebergs():
        attack = ice.iceberg.penguin_amount - ice.peng_amount + \
                 (ice.iceberg.penguins_per_turn+1)*calc_real_dis(enemy_ice, ice.iceberg) \
                 + final_penguins_num(game, enemy_ice)
        if attack * -1 > max_attack:
            max_attack = attack * -1
    redundant = ice.peng_amount - max_attack - 1
    if redundant <= 0:
        return -1
    return redundant + 1


def threat(game):

    threats = []
    for enemy_ice in game.get_enemy_icebergs():
        count = 0
        for ice in game.get_my_icebergs():
            attack = ice.penguin_amount + ice.penguins_per_turn * calc_real_dis(enemy_ice, ice)\
                     - enemy_ice.penguin_amount
            if attack < 0:
                count += 1
            if count == 2:
                break
        if count == 2:
            threats.append(enemy_ice)
    return threats


def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    
    # struct for the items in positive_icebergs and negative_icebergs
    # contains the iceberg itself and the amount of redundant / needed penguins
    class myIce:
        def __init__(self, iceberg, peng_amount, turn=-1, status=""):
            self.iceberg = iceberg
            self.peng_amount = peng_amount
            self.turn = turn
            self.status = status

        def __str__(self):
            return 'iceberg: ' + str(self.iceberg) + ' , peng_amount: ' + str(self.peng_amount) + ' , turn: ' + str(self.turn) + ' , status: ' + str(self.status)
        
    # GLOBAL PARAMETERS
    SPARE = 1
    ICEBERGS = len(game.get_all_icebergs())
    DISTANCE = int(global_dis(game))
    MY_LEVEL = sum_levels(game.get_my_icebergs())
    ENEMY_LEVEL = sum_levels(game.get_enemy_icebergs())
    MY_SUM = sum_peng(game.get_my_icebergs())
    ENEMY_SUM = sum_peng(game.get_enemy_icebergs())
    threats = threat(game)
    bonus = game.get_bonus_iceberg()
    passive_icebergs = game.get_my_icebergs()
    
    if ICEBERGS == 5:
        DISTANCE = 1000
    
    FRONT_INIT_LEN = int(ICEBERGS / 2)
    if (ICEBERGS != 10 and ICEBERGS != 8) or (ICEBERGS == 10 and not bonus):
        FRONT_INIT_LEN = ICEBERGS
    
    front = new_front(game, FRONT_INIT_LEN)
    min_front = minimal_front(game, FRONT_INIT_LEN)
    base_iceberg = base_ice(game)
    
    if ICEBERGS == 12:
        edgs = []
        temp = []
        for ice in game.get_my_icebergs():
            if is_edge(game, ice):
                edgs.append(ice)
        for e in edgs:
            temp.append(e)
            e_neighbors = neighbors(game, e)
            temp += e_neighbors
            for e_nei in e_neighbors:
                if e_nei not in game.get_enemy_icebergs():
                    for e_nei_nei in neighbors(game, e_nei):
                        if e_nei_nei in game.get_enemy_icebergs():
                            temp.append(e_nei_nei)
                            break
        front = []
        [front.append(x) for x in temp if x not in front]
        min_front = front[:]
        FRONT_INIT_LEN = 12
    
    # check which of my icebergs has redundant penguins
    positive_icebergs = []
    for my_iceberg in game.get_my_icebergs():
        redundant = calc_redundant_penguins(game, my_iceberg, MY_LEVEL, ENEMY_LEVEL, MY_SUM, ENEMY_SUM, threats)
        if redundant > 0:
            positive_icebergs.append(myIce(my_iceberg, redundant))

    # build "negative_icebergs" list
    negative_icebergs, useless_icebergs, neutral_icebergs = build_negative_list(game, positive_icebergs, myIce)

    # prevent tie score
    if ICEBERGS == 5 and game.turn > 250 and len(game.get_neutral_icebergs()) == 3:
        pos = game.get_my_icebergs()[0]
        neu = sorted(game.get_neutral_icebergs(), key=lambda x: x.get_turns_till_arrival(pos))[0]
        ddd = calc_illuse_dis(pos, neu)
        amount = pos.penguin_amount - pos.bridge_cost + 1
        if 300-ddd == game.turn:
            pos.send_penguins(neu, amount)
        if 300-ddd+1 == game.turn:
            pos.create_bridge(neu)
        if 300-ddd <= game.turn:
            return
    
    if game.turn == 260 and len(game.get_my_icebergs()) == len(game.get_enemy_icebergs()) and\
            len(game.get_my_icebergs()) >= 2 and MY_LEVEL == ENEMY_LEVEL:
        poss = sorted(game.get_my_icebergs(), key=lambda x: x.penguin_amount)
        pos1 = poss[-1]
        pos2 = poss[-2]
        negs = sorted(game.get_enemy_icebergs(), key=lambda x: x.penguin_amount)
        neg1 = negs[0]
        neg2 = negs[1]
        pos1.send_decoy_penguins(neg1, neg2, int(pos1.penguin_amount/pos1.decoy_cost_factor)-1)
        pos2.send_decoy_penguins(neg1, neg2, int(pos2.penguin_amount/pos2.decoy_cost_factor)-1)

    icebergs2 = positive_icebergs[:]
    
    # upgrade
    if (float(len(game.get_enemy_icebergs()))/ICEBERGS) <= 0.5 and ICEBERGS != 5:
        # upgrade if you can
        positive = positive_icebergs[:]
        for ice in positive:
            if ICEBERGS == 12:
                if is_edge(game, ice.iceberg):
                    continue
            if ice.iceberg.upgrade_cost <= predict_attack(game, ice, min_front, front) and \
                    ice.iceberg.level < ice.iceberg.upgrade_level_limit and not \
                    front_need_help_from_you(game, ice, front, negative_icebergs, DISTANCE):
                ice.iceberg.upgrade()
                positive_icebergs.remove(ice)
        
        # do nothing if you are not upgraded
        if ICEBERGS != 12:
            positive = positive_icebergs[:]
            for ice in positive:
                if ice.iceberg.penguins_per_turn == 1 and not \
                        front_need_help_from_you(game, ice, front, negative_icebergs, DISTANCE):
                    positive_icebergs.remove(ice)
                    icebergs2.remove(ice)
    
    if MY_LEVEL < ENEMY_LEVEL:
        front = min_front
    
    # bonus
    if bonus:
        if not game.get_my_bonus_iceberg() and not game.get_neutral_bonus_iceberg() and len(front) == ICEBERGS:
            positive_icebergs = attackby1(positive_icebergs, bonus, game, DISTANCE, SPARE)

    # build_ bridges
    positive_icebergs = build_bridges(game, positive_icebergs, negative_icebergs)
    
    positive_icebergs2 = positive_icebergs[:]

    # attack and protect
    attack_and_protect(game, positive_icebergs, negative_icebergs, DISTANCE, SPARE, front)
    
    base = []
    for ice in positive_icebergs:
        if ice.iceberg.equals(base_iceberg):
            base = ice
            break

    # team work
    positive_icebergs, negative_icebergs = team_work(game, positive_icebergs, negative_icebergs,
                                                     DISTANCE, SPARE, front, min_front, base)
    
    # attack neutrals
    if ICEBERGS != 5 or len(neutral_icebergs) != 3:
        do_neutral(positive_icebergs, negative_icebergs, neutral_icebergs, game, DISTANCE, SPARE, front, min_front)
    
    if ICEBERGS == 5:
        positive = positive_icebergs[:]
        for ice in positive:
            if ice.iceberg.upgrade_cost <= predict_attack(game, ice, min_front, front) and \
                    ice.iceberg.level < ice.iceberg.upgrade_level_limit and not \
                    front_need_help_from_you(game, ice, front, negative_icebergs, DISTANCE):
                ice.iceberg.upgrade()
                positive_icebergs.remove(ice)
    
    # send reinforcements
    reinforcement(game, positive_icebergs, negative_icebergs, DISTANCE)
    if ICEBERGS != 5:
        upgrade_reinforcement(game, positive_icebergs2, front, DISTANCE)

    for pos in icebergs2:
        if pos not in positive_icebergs:
            passive_icebergs.remove(pos.iceberg)
    
    temp5 = battlefront(game)[0]
    enemy = game.get_enemy_icebergs()
    enemy = sorted(enemy, key=lambda x: x.get_turns_till_arrival(temp5))[0]
    for ice in passive_icebergs:
        if ice.penguin_amount == ice.max_penguins:
            if ice in positive_icebergs:
                amount_to_send = [x.peng_amount for x in positive_icebergs if x.iceberg.equals(ice)][0]
            else:
                amount_to_send = ice.penguins_per_turn
            ice.send_penguins(enemy, ice.penguins_per_turn)
