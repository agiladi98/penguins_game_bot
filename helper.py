# This is a file to helper functions
import math


def generate_num_icebergs(i_num, l):
    """
    a helper function to build and return all of the subset of icebergs and i_num >= len(subset)
    """
    base = []
    lists = [base]
    for i in range(len(l)):
        orig = lists[:]
        new = l[i]
        for j in range(len(lists)):
            if len(lists[j]) <= i_num:
                lists[j] = lists[j] + [new]
        lists = orig + lists

    lists = list(filter(lambda lst: len(lst) == i_num, lists))
    return lists
    
    
def calc_max_dis(icebergs):
    """
    this function calculate and return the maximum distance between the icebergs in the game
    """
    n = len(icebergs)
    m = -1
    for i in range(n):
        for j in range(i+1, n):
            m = max(m, icebergs[i].get_turns_till_arrival(icebergs[j]))
    return m
    

def average_peng(icebergs):
    """
    this function calc the average of the penguin amount to a list of icebergs
    """
    if not icebergs:
        return 0
    return int(sum([i.penguin_amount for i in icebergs])/len(icebergs))

    
def sum_levels(icebergs):
    sm = 0
    for ice in icebergs:
        sm += ice.penguins_per_turn
    return sm


def sum_peng(icebergs):
    sm = 0
    for ice in icebergs:
        sm += ice.penguin_amount
    return sm


def find_bridge(source, destination):
    """
    this fuction get source and destination and find their bridge,
    if the bridge is not exist the function return None
    """
    
    for b in source.bridges:
        if destination in b.get_edges():
            return b
    return None


def calc_real_dis(source, destination):
    """
    this function calc the distance include the bridges.
    """
    dis = source.get_turns_till_arrival(destination)
    b = find_bridge(source, destination)
    if not b:
        b = find_bridge(destination, source)
        if not b:
            return dis
    if b.duration >= dis/b.speed_multiplier:
        return int(dis/b.speed_multiplier)
        
    real_dis = b.duration + (dis-int(b.duration*b.speed_multiplier))
    return real_dis
 
    
def calc_illuse_dis(source, destination):
    """
    this function calc the distance include the bridges.
    """
    dis = source.get_turns_till_arrival(destination)
    duration = source.max_bridge_duration
    if duration >= dis/source.bridge_speed_multiplier:
        return int(dis/source.bridge_speed_multiplier)
        
    real_dis = duration + (dis-int(duration*source.bridge_speed_multiplier))
    return real_dis

    
def real_turn_teal_arrival(group):

    dis = group.turns_till_arrival
    b = find_bridge(group.source, group.destination)
    if not b:
        return dis
    duration = b.duration - 1
    if duration >= dis/b.speed_multiplier:
        x = dis/b.speed_multiplier
        return int(x) + (1 if x - int(x) > 0 else 0)
    return duration + (dis-int(duration*b.speed_multiplier))

    
def illusion_turn_teal_arrival(group):

    dis = group.turns_till_arrival
    duration = group.source.max_bridge_duration - 1
    if duration >= dis/group.source.bridge_speed_multiplier:
        x = dis/group.source.bridge_speed_multiplier
        return int(x) + (1 if x - int(x) > 0 else 0)
    return duration + (dis-int(duration*group.source.bridge_speed_multiplier))
    

def final_penguins_num(game, ice, my_arrival_turn=300, my_amount=0, until_turn=300):
    """
    return the number of penguins on "ice" after all the penguins groups that heading toward it will arive
    negative number - penguins belong to the enemy
    positive number - penguins belong to me
    "until_turn" - optional parameter to determine how many turns to check
    """
    if ice in game.get_my_icebergs():
        status = "mine"
    elif ice in game.get_neutral_icebergs():
        status = "neutral"
    else:
        status = "enemy"
    my_penguin_amount = ice.penguin_amount
    if status == "enemy":
        my_penguin_amount *= -1
    last_group_turns_till_arrival = 0
    groups_toward_ice = [g for g in game.get_all_penguin_groups() if g.destination.equals(ice)]
    groups_toward_ice.sort(key=lambda g: real_turn_teal_arrival(g))
    for g in groups_toward_ice:
        if g in game.get_my_decoy_penguin_groups():
            continue
        g_arrival_turn = real_turn_teal_arrival(g)
        if last_group_turns_till_arrival < my_arrival_turn < g_arrival_turn:
            if status == "mine":
                my_penguin_amount += (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn
            elif status == "enemy":
                my_penguin_amount -= (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn
            my_penguin_amount += my_amount
            if my_penguin_amount > 0:
                status = "mine"
            elif my_penguin_amount == 0:
                status = "neutral"
            else:
                status = "enemy"
            last_group_turns_till_arrival = my_arrival_turn
        
        if until_turn < g_arrival_turn:
            return my_penguin_amount
            
        if status == "mine":
            my_penguin_amount += (g_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn
        elif status == "enemy":  # or status=="neutral":
            my_penguin_amount -= (g_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn

        if g in game.get_enemy_penguin_groups():
            my_penguin_amount -= g.penguin_amount
        else:
            my_penguin_amount += g.penguin_amount

        if my_penguin_amount > 0:
            status = "mine"
        elif my_penguin_amount == 0:
            status = "neutral"
        else:
            status = "enemy"
        last_group_turns_till_arrival = g_arrival_turn

    if my_arrival_turn == 300 or my_arrival_turn < last_group_turns_till_arrival or status == "neutral":
        return my_penguin_amount
    else:
        if status == "mine":
            return my_penguin_amount + (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn
        else:
            return my_penguin_amount - (my_arrival_turn - last_group_turns_till_arrival) * ice.penguins_per_turn

                
def dfs(visited, graph, node, res):
    """
    kind of dfs algorithm , return set of the icebergs that have a path from node
    """
    if node not in visited:
        res.add(node)
        visited.add(node)
        for neighbour in graph[node]:
            res = res.union(dfs(visited, graph, neighbour, res))
    return res
                
                 
def good_distance(game, d):
    """
    return T/F if we can arrive from any iceberg to any iceberg with distance d.
    """
    graph = {}
    icebergs = game.get_all_icebergs()
    
    for ice in icebergs:
        graph[ice] = []
    
    for ice1 in icebergs:
        for ice2 in icebergs:
            if ice1.get_turns_till_arrival(ice2) <= d:
                graph[ice1] += [ice2]
    
    res = dfs(set(), graph, icebergs[0], set())
    
    for ice in icebergs:
        if ice not in res:
            return False
    return True


def global_dis(game):
    d = int(0.6*calc_max_dis(game.get_all_icebergs()))
    while not good_distance(game, d):
        d = int(1.1*d)
    return d
                

def some(g, groups):
    if g not in groups:
        return real_turn_teal_arrival(g)
    return illusion_turn_teal_arrival(g)


def final_penguins_num2(game, ice, my_arrival_turn=-1, groups=[]):
    """
    return the number of penguins on "ice" after all the penguins groups that heading toward it will arive
    negative number - penguins belong to the enemy
    positive number - penguins belong to me
    "until_turn" - optional parameter to determine how many turns to check
    """
    if ice in game.get_my_icebergs():
        status = "mine"
    elif ice in game.get_neutral_icebergs():
        status = "neutral"
    else:
        status = "enemy"
    my_penguin_amount = ice.penguin_amount
    if status == "enemy":
        my_penguin_amount *= -1
    last_group_turns_till_arrival = 0
    groups_toward_ice = [g for g in game.get_all_penguin_groups() if g.destination.equals(ice)]
    groups_toward_ice.sort(key=lambda g: some(g, groups))
    
    temp = groups_toward_ice[:]
    for g in temp:
        if g not in groups:
            total_d = calc_real_dis(g.source, ice)
        else:
            total_d = calc_illuse_dis(g.source, ice)
        kizuz = [grp for grp in game.get_all_penguin_groups() if grp.source.equals(ice) and grp.destination.equals(g.source)]
        for k in kizuz:
            if g not in groups:
                g_turn_till_arrival = real_turn_teal_arrival(g)
            else:
                g_turn_till_arrival = illusion_turn_teal_arrival(g)
            if real_turn_teal_arrival(k) + g_turn_till_arrival >= total_d: 
                kiz = g.penguin_amount - k.penguin_amount
                if kiz < 0:
                    kiz = 0
                g.penguin_amount = kiz
                groups_toward_ice[groups_toward_ice.index(g)].penguin_amount = kiz

    for g in groups_toward_ice:
        if g in game.get_my_decoy_penguin_groups():
            continue
        if g not in groups:
            g_turn_till_arrival = real_turn_teal_arrival(g)
        else:
            g_turn_till_arrival = illusion_turn_teal_arrival(g)
        
        if status == "mine":
            my_penguin_amount += (g_turn_till_arrival - last_group_turns_till_arrival) * ice.penguins_per_turn
        elif status == "enemy":  # or status=="neutral":
            my_penguin_amount -= (g_turn_till_arrival - last_group_turns_till_arrival) * ice.penguins_per_turn
          
        if g in game.get_enemy_penguin_groups():
            my_penguin_amount -= g.penguin_amount
        else:
            my_penguin_amount += g.penguin_amount
        
        if my_penguin_amount > 0:
            status = "mine"
        elif my_penguin_amount == 0:
            status = "neutral"
        else:
            status = "enemy"
        last_group_turns_till_arrival = g_turn_till_arrival
    
    return my_penguin_amount, last_group_turns_till_arrival, status
    
    
def calc_redundant_penguins(game, ice, my_level, enemy_level, my_penguin_sum, enemy_penguin_sum, threats):
    """
    return the number of penguins that are not needed for self defense (consider all enemy groups)
    negative value means that there is no redundant penguins
    """
    my_penguin_amount = ice.penguin_amount
    if my_level <= 1.5 * enemy_level or my_penguin_sum <= 1.5 * enemy_penguin_sum:
        for enemy_ice in game.get_enemy_icebergs():
            if enemy_ice not in threats:
                attack = my_penguin_amount + ice.penguins_per_turn * calc_real_dis(enemy_ice, ice) - enemy_ice.penguin_amount
                if attack < 0:
                    return -1
    
    redundant = 1000
    enemy_penguin_groups = [group for group in game.get_enemy_penguin_groups() if group.destination.equals(ice)]
    enemy_penguin_groups.sort(key=lambda group: real_turn_teal_arrival(group))
    last_group_turns_till_arrival = 0
    temp = my_penguin_amount
    for group in enemy_penguin_groups:
        temp += ice.penguins_per_turn * (real_turn_teal_arrival(group) - last_group_turns_till_arrival) - group.penguin_amount
        if temp < redundant:
            redundant = temp
            if redundant <= 0:
                return -1
        last_group_turns_till_arrival = real_turn_teal_arrival(group)
    redundant -= 1
    if redundant > my_penguin_amount:
        redundant = my_penguin_amount
        
    return redundant


def max_flow(C, s, t):
    """
        Edmonds-Karp Algorithm

        :param C: 'capacity' of the network
        :param s: source
        :param t: 'pit'
        :return: max flow (network)
    """
    n = len(C)  # C is the capacity matrix
    F = [[0] * n for i in xrange(n)]
    path = bfs(C, F, s, t)
    while not path:
        flow = min(C[u][v] - F[u][v] for u, v in path)
        for u, v in path:
            F[u][v] += flow
            F[v][u] -= flow
        path = bfs(C, F, s, t)
    return F


def bfs(C, F, s, t):
    """
    find path by using BFS
    """
    queue = [s]
    paths = {s: []}
    if s == t:
        return paths[s]
    while queue:
        u = queue.pop(0)
        for v in xrange(len(C)):
                if C[u][v]-F[u][v] > 0 and v not in paths:
                    paths[v] = paths[u]+[(u, v)]
                    if v == t:
                        return paths[v]
                    queue.append(v)
    return None


def iceberg2rmv(flow, graph_negative, ice2index, t):
    return ice2index[min(graph_negative.keys(), key=lambda x:flow[ice2index[x]][t]/x.peng_amount)]
