from helper import *
from rearFront import *


def final_penguins_num_for_neutral(game, ice, my_arrival_turn=-1, until_turn=300, groups=[]):
    """
    return the number of penguins on "ice" after all the penguins groups that heading toward it will arrive,
    and a flag to state if "ice" is still neutral in the end
    negative number - penguins belong to the enemy
    positive number - penguins belong to me or to nobody
    "until_turn" - optional parameter to determine how many turns to check
    """
    status = "neutral"
    last_status = status
    my_penguin_amount = ice.penguin_amount
    last_group_turns_till_arrival = 0
    groups_toward_ice = [g for g in game.get_all_penguin_groups() if g.destination.equals(ice)]
    groups_toward_ice.sort(key=lambda g: some(g, groups))
    for g in groups_toward_ice:
        
        if g not in groups:
            g_turn_till_arrival = real_turn_teal_arrival(g)
        else:
            g_turn_till_arrival = illusion_turn_teal_arrival(g)
        
        if g_turn_till_arrival >= until_turn:
            return status == "neutral"

        if status == "mine":
            my_penguin_amount += (g_turn_till_arrival - last_group_turns_till_arrival) * ice.penguins_per_turn
        elif status == "enemy":
            my_penguin_amount -= (g_turn_till_arrival - last_group_turns_till_arrival) * ice.penguins_per_turn

        if g_turn_till_arrival == last_group_turns_till_arrival and last_status == "neutral":
            aaa = g.penguin_amount
            if g in game.get_enemy_penguin_groups():
                aaa *= -1
            my_penguin_amount = last_group_amount+aaa

        if status == "neutral" and g_turn_till_arrival != last_group_turns_till_arrival:
            my_penguin_amount -= g.penguin_amount
            if my_penguin_amount < 0:
                if g in game.get_my_penguin_groups():
                    my_penguin_amount *= -1
            else:
                last_group_turns_till_arrival = g_turn_till_arrival
                last_group_amount = g.penguin_amount
                last_status = status
                if g in game.get_enemy_penguin_groups():
                    last_group_amount *= -1
                continue
        else:
            if g in game.get_enemy_penguin_groups():
                my_penguin_amount -= g.penguin_amount
            else:
                my_penguin_amount += g.penguin_amount
                
        last_group_turns_till_arrival = g_turn_till_arrival
        last_group_amount = g.penguin_amount
        last_status = status
        if g in game.get_enemy_penguin_groups():
            last_group_amount *= -1
        
        if my_penguin_amount > 0:
            status = "mine"
        elif my_penguin_amount == 0:
            status = "neutral"
        else:
            status = "enemy"

    if until_turn != 300:
        return status == "neutral"
    if status == "neutral":
        return my_penguin_amount, True
    elif my_arrival_turn == -1 or my_arrival_turn < last_group_turns_till_arrival:
        return my_penguin_amount, False
    else:
        if status == "mine":
            return my_penguin_amount + (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn, False
        else:
            return my_penguin_amount - (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn, False


def do_neutral(positive_icebergs, negative_icebergs, neutral_icebergs, game, DISTANCE, SPARE, front, min_front):
    for my_ice in positive_icebergs:
        can = False
        
        neutral_icebergs.sort(key=lambda x: calc_real_dis(my_ice.iceberg, x) + x.penguin_amount)
        for ice in neutral_icebergs:
            if ice not in front:
                continue
            flag = True
            if len(min_front) != len(game.get_all_icebergs()):
                for f in min_front:
                    if f in neutral_icebergs and f.penguins_per_turn > ice.penguins_per_turn and \
                            calc_real_dis(my_ice.iceberg, f) < DISTANCE:
                        flag = False
                        break
            if flag:
                amount = ice.penguin_amount + SPARE
                if ice not in min_front or front_need_help(game, min_front, negative_icebergs, DISTANCE):
                    amount += 20
                else:
                    for ene in game.get_enemy_icebergs():
                        if abs(calc_real_dis(ene, ice)-calc_real_dis(my_ice.iceberg, ice)) < 5:
                            amount += ene.penguin_amount
                            break
                if my_ice.peng_amount + SPARE > amount and my_ice.peng_amount > amount + SPARE and \
                        DISTANCE > calc_real_dis(my_ice.iceberg, ice):
                    dest = ice
                    can = True
                    break
        if can:
            my_ice.iceberg.send_penguins(dest, amount)
            positive_icebergs.remove(my_ice)
            neutral_icebergs.remove(dest)
    return positive_icebergs, neutral_icebergs
