import numpy
import networkx
import netgraph
import matplotlib.pyplot as plt
import copy

import randomizer
from randomizer import Item,Hm,Badge,Rule


class Player:
    def __init__(self):
        self.level = 5;
        self.exp = 0;
        self.location = "";
        self.key_items = [];
        self.completed_checks = [];
        self.visited_locations = set();

    def get_item(self,item):
        self.key_items.append(item);
    def go_to_location(self,location):
        self.location = location
        self.visited_locations.add(location)
        return
    # running is 8 tiles/sec, bike is 16 tiles/sec
    def speed(self):
        if Item.BICYCLE in self.key_items: return 16;
        return 8;
    def gain_exp(self,exp):
        if self.level>=100: return
        self.exp += exp;
        lvl_up_exp = Player.level_exp(self.level+1)-Player.level_exp(self.level)
        while self.exp >= lvl_up_exp:
            self.level+=1
            self.exp %= lvl_up_exp
            lvl_up_exp = Player.level_exp(self.level+1)-Player.level_exp(self.level)
        return
    # use medium slow experience group
    @staticmethod
    def level_exp(level):
        return 6/5*level**3 - 15*level**2 +100*level-140;

class Game:
    def __init__(self,locations):
        self.locations = locations;
        self.graph = networkx.Graph();
        for l in locations:
            self.graph.add_node(l.name,location=l)
        for l in locations:
            for (loc,steps) in l.steps_to.items():
                self.graph.add_edge(l.name,loc,steps=steps)
        self.player = Player();
        self.player.go_to_location('New Bark Town');
        # cumulative time spent playing
        self.time = 0;
        return

    # get possible checks for the player that have not been visited 
    def get_accessible_checks(self):
        items = self.player.key_items
        return randomizer.accessible_checks(self.locations,items,is_player=True)[0]
    # possible locations that the player can reach
    def get_accessible_locations(self):
        items = self.player.key_items
        return randomizer.accessible_locations(self.locations,items,is_player=True)
    # possible checks at the player's location
    def get_checks_here(self):
        logic = randomizer.in_logic(self.player.key_items,is_player=True)
        chks = self.graph.nodes[self.player.location]['location'].unrevealed_checks()
        valid_chks = []
        for chk in chks:
            if len(chk.rules)==0: valid_chks.append(chk); continue;
            for rule in chk.rules:
                if set(rule).issubset(logic): valid_chks.append(chk); break;
        return valid_chks
    # possible locations immediately accessible from the player's location
    def get_neighboring_locations(self):
        acc_locations = self.get_accessible_locations();
        locs = [];
        for neighbor in self.graph.neighbors(self.player.location):
            if neighbor in acc_locations:
                locs.append(neighbor)
        logic = randomizer.in_logic(self.player.key_items,is_player=True)
        if Rule.CANUSEFLY in logic:
            for l in self.player.visited_locations:
                loc = self.graph.nodes[l]['location']
                if loc.fly_point and not l in locs:
                    locs.append(l)
        # hotfix for backwards kanto but no snorlax
        if self.player.location=='Vermilion City':
            if Rule.SNORLAX not in self.player.key_items:
                if 'Pewter City' in locs:
                    locs.remove('Pewter City')
        return locs
    # attempt a check, returns the item and cost 
    # item is None if check is failed or check is not valid (check_logic has to be True)
    def attempt_check(self,check,check_logic=False):
        if check_logic:
            if check not in self.get_checks_here(): return (None,0)
        (item,cost) = check.attempt(self.player)
        self.time += cost
        return (item,cost)
    # attempt to go to a location, return bool(successful) and cost
    # go to location is successful if location is a neighboring location or fly point and can fly, and logic is set
    def go_to_location(self,location,check_logic=False):
        logic = randomizer.logical_rules(self.player.key_items);
        if check_logic:
            if Rule.CANUSEFLY in logic and location in self.player.visited_locations:
                # fly speed is considered to take 2 secs
                self.player.go_to_location(location)
                return (location,2);
            if location not in self.accessible_locations(): return (False,0);
            if location not in self.get_neighboring_locations(): return (None,0);

        if Rule.CANUSEFLY in logic and location in self.player.visited_locations:
            # fly speed is considered to take 2 secs
            self.player.go_to_location(location)
            self.time += 2
            return (location,2);
        
        if location in self.graph.neighbors(self.player.location):
            steps = self.graph.edges[self.player.location,location]['steps']
            cost = steps/self.player.speed()
            succeed,cost_battle = self.graph.nodes[location]['location'].attempt(self.player)
            cost += cost_battle
            if not succeed:
                return (None,cost)

            self.player.go_to_location(location)
            self.time += cost
            return(location,cost)
        nodes = networkx.shortest_path(self.graph,self.player.location,location)
        cost = 0;
        for edge in zip( nodes,nodes[1:] ):
            cost += self.graph.edges[edge]['steps']/self.player.speed()
            succeed,cost_battle = self.graph.nodes[edge[1]]['location'].attempt(self.player)
            cost += cost_battle
            if not succeed:
                return (self.player.location,cost)
            self.player.go_to_location(edge[1])
        self.time += cost
        return (location,cost)
    def attempt_action(self,action,check_logic=False):
        if isinstance(action,randomizer.Check):
            return self.attempt_check(action,check_logic)
        if isinstance(action,str):
            return self.go_to_location(action,check_logic)
        raise Exception('action not a check or location name').with_traceback(tracebackobj)

    def is_finished(self):
        return Rule.BEATRED in self.player.key_items;
    def plot(self):
        locations = self.locations
        coords = dict(zip([l.name for l in locations],[l.coord for l in locations]))
        labels = dict(zip([l.name for l in locations],[l.name for l in locations]))
        annotations = dict()
        for l in locations:
            str = ''
            for chk in l.checks:
                if chk.item_count>0:
                    str+= chk.action + ' : ' + ';'.join([item.name for item in chk.item]) + '\n'
            annotations[l.name]=str
        
        IG = netgraph.InteractiveGraph(self.graph, node_labels=True, node_label_fontdict=dict(size=10,fontweight='bold'),
                                    node_layout=coords, 
                                    node_size=5000, node_label_offset=100, edge_width=1000, 
                                    node_shape = 'o', node_edge_color='blue', node_edge_width=1000,
                                    annotations=annotations, annotation_fontdict = dict(fontsize=8))
        plt.show()


def create(count=1,verbose=False):
    randos = []
    locs = randomizer.read_json()
    for i in range(count):
        locations = copy.deepcopy(locs)
        randomizer.randomize(locations,verbose)
        rando = Game(locations)
        if count==1: return rando
        randos.append(rando)
    return randos

def is_item(item):
    if isinstance(item,Item) or \
            isinstance(item,Hm) or\
            isinstance(item,Badge) or\
            isinstance(item,Rule):
                return True
    return False;
# note that for now most location interface is just names(str) and not Location objects which are accessible via game.graph.nodes[name]['location']
def is_location(loc):
    if isinstance(loc,str): return True
    return False
