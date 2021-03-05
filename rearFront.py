from helper import *


def battlefront(game):
    min_distance = 1000
    battlefront = []
    my_ices = game.get_my_icebergs()
    for i in range(2):
        front_ice = []
        for enemy_ice in game.get_enemy_icebergs():
            for my_ice in my_ices:
                distance = calc_real_dis(enemy_ice, my_ice)
                if distance < min_distance:
                    min_distance = distance
                    front_ice = my_ice
        if front_ice:
            battlefront.append(front_ice)
            my_ices.remove(front_ice)
            min_distance = 1000
    return battlefront


def base_ice(game):
    mx = 0
    base = []
    for ice in game.get_neutral_icebergs() + game.get_my_icebergs():
        for enemy_ice in game.get_enemy_icebergs():
            distance = ice.get_turns_till_arrival(enemy_ice)
            if distance > mx:
                mx = distance
                base = ice
    return base


def new_front(game, FRONT_INIT_LEN):
    rear = []
    base = base_ice(game)
    flag = False
    icebergs = game.get_all_icebergs()
    icebergs.sort(key=lambda x: x.get_turns_till_arrival(base))

    for ice in icebergs[:FRONT_INIT_LEN]:
        rear.append(ice)
        if ice not in game.get_my_icebergs():
            flag = True
     
    if flag:
        return rear
  
    return icebergs


def upgrade_reinforcement(game, positive_icebergs, front, DISTANCE):

    if sum_levels(game.get_my_icebergs()) < sum_levels(game.get_enemy_icebergs()):
        temp = sorted(game.get_my_icebergs(), key=lambda x: x.penguins_per_turn)
        lev = temp[0].penguins_per_turn
        index = 0
        for ice in temp:
            if ice.penguins_per_turn > lev:
                break
            index += 1
        poor = temp[:index]
        good = temp[index:]
        for pos in positive_icebergs:
            if pos.iceberg in good:
                poor.sort(key=lambda x: x.get_turns_till_arrival(pos.iceberg))
                for poor_ice in poor:
                    if poor_ice.get_turns_till_arrival(pos.iceberg) > DISTANCE:
                        break
                    if pos.iceberg.penguin_amount == pos.iceberg.max_penguins:
                        amount_to_send = pos.iceberg.penguins_per_turn
                    else:
                        amount_to_send = 1
                    if pos.iceberg.can_send_penguins(poor_ice, amount_to_send):
                        pos.iceberg.send_penguins(poor_ice, amount_to_send)
                        break


def reinforcement(game, positive_icebergs, negative_icebergs, DISTANCE):
    
    avg_amount = average_peng(game.get_enemy_icebergs())
    my_level = sum_levels(game.get_my_icebergs())
    enemy_level = sum_levels(game.get_enemy_icebergs())
    my_penguin_sum = sum_peng(game.get_my_icebergs())
    enemy_penguin_sum = sum_peng(game.get_enemy_icebergs())
    positive = positive_icebergs[:]
    front = battlefront(game)

    for ice in positive:
        flag = True
        max_attack = 0
        for enemy_ice in game.get_enemy_icebergs():
            attack = ice.iceberg.penguin_amount - ice.peng_amount + \
                     ice.iceberg.penguins_per_turn*calc_real_dis(enemy_ice, ice.iceberg) - enemy_ice.penguin_amount
            if attack * -1 > max_attack:
                max_attack = attack * -1
        redundant = ice.peng_amount - max_attack - 1
        if my_penguin_sum > 1.5 * enemy_penguin_sum and my_penguin_sum - enemy_penguin_sum > 200:
            amount_to_send = ice.peng_amount / 4
        else:
            amount_to_send = min(ice.iceberg.penguin_amount - avg_amount, redundant)
        if amount_to_send <= 0 or ice.iceberg.penguins_per_turn < 4:
            flag = False
        for neg in negative_icebergs:
            if neg.iceberg in game.get_my_icebergs() and calc_real_dis(ice.iceberg, neg.iceberg) < DISTANCE:
                flag = False
                break
        for neu in game.get_neutral_icebergs():
            if calc_real_dis(ice.iceberg, neu) < DISTANCE:
                flag = False
                break
        if not flag and ice.iceberg.penguin_amount == ice.iceberg.max_penguins:
            flag = True
            amount_to_send = ice.iceberg.penguins_per_turn
        if ice.iceberg in front:
            flag = False
        if flag:
            count = 0 
            for my_ice in front:
                if calc_real_dis(my_ice, ice.iceberg) < DISTANCE:
                    count += 1
            if count:
                part_amount = int(amount_to_send / count)
                if part_amount < 3:
                    part_amount = amount_to_send
                    flag = False
                for my_ice in front:
                    if my_ice.penguin_amount == my_ice.max_penguins:
                        continue
                    if part_amount and calc_real_dis(my_ice, ice.iceberg) < DISTANCE:
                        ice.iceberg.send_penguins(my_ice, part_amount)
                        if ice in positive_icebergs:
                            positive_icebergs.remove(ice)
                        if not flag:
                            break


def front_need_help_from_you(game, ice, front, negative_icebergs, DISTANCE):

    if len(front) != len(game.get_all_icebergs()):
        for neg in negative_icebergs:
            if neg.iceberg in front and neg.iceberg.get_turns_till_arrival(ice.iceberg) < DISTANCE:
                return True
    return False
    
    
def front_need_help(game, front, negative_icebergs, DISTANCE):
    """
    if sum_levels(game.get_my_icebergs()) < sum_levels(game.get_enemy_icebergs()):
        return True
    """
    if len(front) == len(game.get_all_icebergs()):
        return False
    for neg in negative_icebergs:
        if neg.iceberg in front and neg.iceberg not in game.get_neutral_icebergs():
            return True
    for red in game.get_enemy_icebergs():
        if red in front:
            return True
    return False
  
    
def minimal_front(game, FRONT_INIT_LEN):
    rear = []
    base = base_ice(game)
    flag = False
    icebergs = game.get_all_icebergs()
    icebergs.sort(key=lambda x: x.get_turns_till_arrival(base))
    
    for ice in icebergs[:FRONT_INIT_LEN]:
        rear.append(ice)
    
    return rear
 
    
def is_edge(game, ice):
    my_icebergs = game.get_my_icebergs()
    icebergs = sorted(game.get_all_icebergs(), key=lambda x: x.get_turns_till_arrival(ice))
    neighbor1 = icebergs[1]
    neighbor2 = icebergs[2]
    if neighbor1 not in my_icebergs or neighbor2 not in my_icebergs:
        return True
    return False


def neighbors(game, ice):
    my_icebergs = game.get_my_icebergs()
    icebergs = sorted(game.get_all_icebergs(), key=lambda x: x.get_turns_till_arrival(ice))
    return icebergs[1:3]
