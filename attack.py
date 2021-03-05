# This is a file to attack functions

from helper import *
from neutrals import *


def attackby1(positive_icebergs, iceberg, game, DISTANCE, SPARE):
    amount = iceberg.penguin_amount + SPARE
    amount += sum([-1*x.penguin_amount if x.source in game.get_my_icebergs() else
                   x.penguin_amount for x in game.get_all_penguin_groups() if x.destination.equals(iceberg)])
    amount += iceberg.max_turns_to_bonus
    
    if amount <= -5*iceberg.max_turns_to_bonus:
        return positive_icebergs
    elif amount <= 0:
        amount = iceberg.max_turns_to_bonus + SPARE
        
    lst=[t for t in positive_icebergs if t.peng_amount>amount]
    lst.sort(key=lambda x: calc_real_dis(x.iceberg, iceberg))
    
    if lst:
        dest = iceberg
        lst[0].iceberg.send_penguins(dest, amount)
        if lst[0].peng_amount-amount > 1:
            positive_icebergs[positive_icebergs.index(lst[0])].peng_amount -= amount
        else:
            positive_icebergs.remove(lst[0])
    else:
        lst = [t for t in positive_icebergs if calc_real_dis(t.iceberg, iceberg) <= DISTANCE*1.2]
        lst.sort(key=lambda x: x.peng_amount)
        if len(lst) > 1:
            for i1 in range(len(lst)):
                for i2 in range(i1+1, len(lst)):
                    if lst[i1].peng_amount + lst[i2].peng_amount >= amount:
                        lst[i1].iceberg.send_penguins(iceberg, lst[i1].peng_amount)
                        lst[i2].iceberg.send_penguins(iceberg,
                                                      amount - lst[i1].peng_amount if amount - lst[i1].peng_amount > 0
                                                      else amount - lst[i1].peng_amount + 1)
                        for indx in [i1, i2]:
                            if lst[indx].peng_amount-amount > 1:
                                positive_icebergs[positive_icebergs.index(lst[indx])].peng_amount -= amount
                            else:
                                positive_icebergs.remove(lst[indx])
                        return positive_icebergs
    return positive_icebergs


def attack_and_protect(game, positive_icebergs, negative_icebergs, DISTANCE, SPARE, front):
    # send penguins from positive_icebergs to negative_icebergs (prefers shortest distances)
    min_distance = DISTANCE
    source = 0
    dest = 0
    min_amount = 0
    bad_pairs = []
    enemy_avg = average_peng(game.get_enemy_icebergs())
    negative_icebergs.sort(reverse=True, key=lambda x: x.iceberg.penguins_per_turn)
    while True:
        for d in negative_icebergs:
            if d.iceberg not in front:
                continue
            for s in positive_icebergs:
                distance = calc_real_dis(s.iceberg, d.iceberg)
                if d.iceberg in game.get_neutral_icebergs():
                    neutral = final_penguins_num_for_neutral(game, d.iceberg, distance, distance)
                    amount = final_penguins_num_for_neutral(game, d.iceberg, distance)[0] * -1
                    # if I will get to d when it is still neutral - do nothing
                    if neutral:
                        continue
                else:
                    if distance < d.turn or d.status == "neutral":
                        amount = d.peng_amount
                        if distance < d.turn and s.peng_amount <= d.peng_amount:
                            X = final_penguins_num(game,d.iceberg,distance,s.peng_amount, 300)
                            if X > 0:
                                amount = s.peng_amount - SPARE
                    elif d.status == "mine":
                        amount = d.peng_amount + (distance - d.turn) * d.iceberg.penguins_per_turn
                    else:
                        amount = d.peng_amount*-1 - (distance - d.turn) * d.iceberg.penguins_per_turn
                        amount *= -1
                    
                if s.peng_amount > amount and distance < min_distance and (s,d) not in bad_pairs:
                    min_distance = distance
                    min_amount = amount
                    source = s
                    dest = d

        if min_distance != DISTANCE and 0 < min_amount < source.peng_amount:
            min_distance = DISTANCE
            for neg in negative_icebergs:
                if neg.iceberg in front:
                    if source.iceberg.get_turns_till_arrival(dest.iceberg)-source.iceberg.get_turns_till_arrival(neg.iceberg) > 5:
                        bad_pairs.append((source, dest))
                        break
            if (source, dest) not in bad_pairs:
                amout_to_send = min_amount + SPARE
                if enemy_avg > amout_to_send and sum_levels(game.get_my_icebergs()) >= sum_levels(game.get_enemy_icebergs()):
                    amout_to_send = min(int(enemy_avg), source.peng_amount)
                source.iceberg.send_penguins(dest.iceberg, amout_to_send)
                positive_icebergs.remove(source)
                negative_icebergs.remove(dest)
                bad_pairs1 = bad_pairs[:]
                for bad in bad_pairs1:
                    if bad[0].iceberg.get_turns_till_arrival(bad[1].iceberg) > bad[0].iceberg.get_turns_till_arrival(dest.iceberg):
                        bad_pairs.remove(bad)
        else:
            break
    

def worth_to_add_bridge(game, source, destination, negative_icebergs):
    """
    this function check if adding a bridge bwtween source and destination worth it
    """
    my_peng_groups = game.get_my_penguin_groups()
    
    relevant = [group for group in my_peng_groups if
                (group.source.equals(source.iceberg) and group.destination.equals(destination))]
    
    if not relevant:
        return False
    
    relevant.sort(key=lambda x: x.turns_till_arrival)
    negative = [ice.iceberg for ice in negative_icebergs]
    
    if destination not in negative and destination in game.get_neutral_icebergs():
        ene_g = [g for g in game.get_enemy_penguin_groups() if g.destination.equals(destination)]
        if ene_g:
            return False
    
    if destination in negative:
        if destination in game.get_neutral_icebergs():
            if final_penguins_num_for_neutral(game, destination, -1, 300, relevant)[0] > 0:
                negative_icebergs.remove([x for x in negative_icebergs if x.iceberg.equals(destination)][0])
                return True
        else:
            if final_penguins_num2(game, destination, -1, relevant)[0] > 0:
                negative_icebergs.remove([x for x in negative_icebergs if x.iceberg.equals(destination)][0])
                return True

    if source.peng_amount - source.iceberg.bridge_cost < 12:
        return False
    if relevant[-1].turns_till_arrival/source.iceberg.bridge_speed_multiplier >= 4 and \
            sum([x.penguin_amount for x in relevant])/source.iceberg.get_turns_till_arrival(destination) >= 0.5:
        return True
    if source.iceberg.get_turns_till_arrival(destination) <= 8 and relevant[-1].turns_till_arrival >= 4 and \
            sum([x.penguin_amount for x in relevant])/source.iceberg.get_turns_till_arrival(destination) >= 1.2:
        return True
    return False


def build_bridges(game, positive_icebergs, negative_icebergs):
    pis = positive_icebergs[:]
    ens = game.get_enemy_icebergs() + game.get_neutral_icebergs()
    for p in pis:
        for n in ens:
            if p.iceberg.can_create_bridge(n) and worth_to_add_bridge(game, p, n, negative_icebergs):
                p.iceberg.create_bridge(n)
                positive_icebergs.remove(p)
                break
    return positive_icebergs


def team_work(game, positive_icebergs, negative_icebergs, DISTANCE, SPARE, front, min_front, base):
    """
    this function attack the the enemy with team work of the positive icebergs
    """
    dst1 = DISTANCE
    fff = False
    i_num = 2
    if negative_icebergs:
        temp = [x.peng_amount for x in negative_icebergs]
        high = max(temp)
        low = min(temp)
        if high != low:
            grade = lambda x: 0.2*(((x.peng_amount-low)/(high-low))*100) + 0.8*((x.iceberg.penguins_per_turn-1)*33.3333)
            negative_icebergs = sorted(negative_icebergs, key=grade)[::-1]
        
        while i_num <= 5 and i_num <= len(positive_icebergs):
            temp_negative = negative_icebergs[::]
            for e in temp_negative:
                if e.iceberg in game.get_neutral_icebergs() or e.iceberg not in front:
                    continue
                if e.iceberg not in min_front:
                    DISTANCE = dst1*(5/6)
                    if base in positive_icebergs:
                        positive_icebergs.remove(base)
                        fff = True
                elif fff:
                    DISTANCE = dst1
                    positive_icebergs.append(base)
                    fff = False
                else:
                    DISTANCE = dst1
                best_group = []
                min_dis = int(DISTANCE*1.25) if i_num < len(positive_icebergs) else DISTANCE*100
                
                for g in generate_num_icebergs(i_num, positive_icebergs):
                    
                    max_group_dis = max([calc_real_dis(i.iceberg, e.iceberg) for i in g])
                    
                    if max_group_dis < min_dis:
                        
                        if max_group_dis < e.turn or e.status == "neutral":
                            amount = e.peng_amount
                        elif e.status == "mine":
                            amount = e.peng_amount + (max_group_dis - e.turn) * e.iceberg.penguins_per_turn
                        else:
                            amount = e.peng_amount*-1 - (max_group_dis - e.turn) * e.iceberg.penguins_per_turn
                            amount *= -1
                        
                        if sum([i.peng_amount for i in g]) > amount + SPARE:
                            min_dis = max_group_dis
                            best_group = g
                        
                if best_group:
                    if min_dis < e.turn or e.status == "neutral":
                        amount = e.peng_amount
                    elif e.status == "mine":
                        amount = e.peng_amount + (min_dis - e.turn) * e.iceberg.penguins_per_turn
                    else:
                        amount = e.peng_amount*-1 - (min_dis - e.turn) * e.iceberg.penguins_per_turn
                        amount *= -1
                    p_count = amount + SPARE
                    best_group.sort(key=lambda x: calc_real_dis(x.iceberg, e.iceberg))
                    cc = 0
                    for ice in best_group:
                        if p_count > 0:
                            if cc == 0 and ice.peng_amount >= p_count:
                                break
                            if ice.peng_amount > 0:
                                
                                if ice.peng_amount <= p_count:
                                    ice.iceberg.send_penguins(e.iceberg, ice.peng_amount)
                                    p_count -= ice.peng_amount
                                    positive_icebergs.remove(ice)
                                    if base and ice.iceberg.equals(base.iceberg):
                                        fff = False
                                else:
                                    ice.iceberg.send_penguins(e.iceberg, p_count)
                                    positive_icebergs[positive_icebergs.index(ice)].peng_amount -= p_count
                                    p_count -= ice.peng_amount
                                    ice = positive_icebergs[positive_icebergs.index(ice)]
                                cc = 1
                        else:
                            break
                    if cc == 1:
                        negative_icebergs.remove(e)
            i_num += 1
    if fff:
        positive_icebergs.append(base)
    return positive_icebergs, negative_icebergs
