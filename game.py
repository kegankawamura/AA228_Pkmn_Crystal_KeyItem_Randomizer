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
    # use medium fast experience group
    @staticmethod
    def level_exp(level):
        return level**3
        #return 6/5*level**3 - 15*level**2 +100*level-140;

class Game:
    def __init__(self,locations=None):
        if locations==None:
            self.locations = None
            self.graph = None
            self.player = None
            self.time = -1;
            return
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
    # in case the check is not directly from this game
    def find_check(self,check):
        checks = self.graph.nodes[check.location]['location'].checks
        return next(c for c in checks if c==check)
    # attempt a check, returns the item and cost
    # item is None if check is failed or check is not valid (check_logic has to be True)
    def attempt_check(self,check,check_logic=False):
        if check_logic:
            if check not in self.get_checks_here(): return (None,0)
        (item,cost) = self.find_check(check).attempt(self.player)
        self.time += cost
        return (item,cost)
    # attempt a check, moving to the location if necessary
    def attempt_accessible_check(self,check,check_logic=False):
        if check in self.get_checks_here(): return self.attempt_check(check)

        location,cost = self.go_to_location(check.location,check_logic)
        if location != check.location: return (location,cost)
        item,cost_check=self.attempt_check(check)
        cost+= cost_check
        return (item,cost)
    # get approximate probability of successfully executing check
    def prob_success(self,check):
        if check in self.get_checks_here(): return self.find_check(check).prob_success(self.player)
        self.conditional_graph()
        nodes = networkx.shortest_path(self.graph,self.player.location,check.location,weight='steps')
        prob = 1;
        for loc in nodes[1:]:
            prob *= self.graph.nodes[loc]['location'].prob_success(self.player)
        prob *= self.find_check(check).prob_success(self.player)
        return prob

    # attempt to go to a location, return bool(successful) and cost
    # go to location is successful if location is a neighboring location or fly point and can fly, and logic is set
    def go_to_location(self,location,check_logic=False):
        # update graph
        self.conditional_graph()
        logic = randomizer.logical_rules(self.player.key_items);
        if check_logic:
            if Rule.CANUSEFLY in logic and location in self.player.visited_locations:
                # fly speed is considered to take 2 secs
                self.player.go_to_location(location)
                return (location,2);
            if location not in self.accessible_locations(): return (None,0);
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
        nodes = networkx.shortest_path(self.graph,self.player.location,location,weight='steps')
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

    # 'removes' conditional paths depending on what the player has
    def conditional_graph(self):
        graph = self.graph;
        if Rule.SNORLAX not in self.player.key_items:
            self.graph.edges[('Vermilion City','Pewter City')]['steps']=9999999
        else:
            self.graph.edges[('Vermilion City','Pewter City')]['steps']=100
        if Item.SQUIRTBOTTLE not in self.player.key_items:
            self.graph.edges[('Ecruteak City','Goldenrod City')]['steps']=9999999
            self.graph.edges[('Ecruteak City','Violet City')]['steps']=9999999
        else:
            self.graph.edges[('Ecruteak City','Goldenrod City')]['steps']=180
            self.graph.edges[('Ecruteak City','Violet City')]['steps']=50

    def is_finished(self):
        return Rule.BEATRED in self.player.key_items;
    def plot(self):
        locations = self.locations
        coords = dict(zip([l.name for l in locations],[l.coord for l in locations]))
        labels = dict(zip([l.name for l in locations],[l.name for l in locations]))
        colors = list()
        for loc in self.graph.nodes():
            l = self.graph.nodes[loc]['location']
            if loc == self.player.location: colors.append('blue')
            elif all([chk.revealed for chk in l.checks]):
                colors.append('green')
            elif any([chk.revealed for chk in l.checks]):
                colors.append('orange')
            else: colors.append('grey')

        #for l in locations:
        #    str = ''
        #    if all([chk.revealed for chk in l.checks]):
        #        colors[l.name] = 'green'
        #    elif any([chk.revealed for chk in l.checks]):
        #        colors[l.name] = 'orange'
        #    else:
        #        colors[l.name] = 'white'
        #    if l.name == self.player.location:
        #        color_player[l.name] = 'blue'
        #        colors[l.name] = 'blue'
            #else: color_player[l.name] = 'white'

        networkx.draw(self.graph, with_labels=True, font_size=10,font_weight='bold',
                                    pos=coords,
                                    node_size=150, width=2,
                                    node_shape = 'o', node_color=colors
                                    )
        plt.ion()
        plt.show()
        plt.pause(.001)

    def plot_interactive(self):
        locations = self.locations
        coords = dict(zip([l.name for l in locations],[l.coord for l in locations]))
        labels = dict(zip([l.name for l in locations],[l.name for l in locations]))
        annotations = dict()
        colors = dict()
        color_player = dict()
        for l in locations:
            str = ''
            for chk in l.checks:
                if chk.item_count>0:
                    if chk.revealed:
                        str+='\N{check mark}'
                    str+= chk.action + ' : ' + ';'.join([item.name for item in chk.item]) + '\n'
            annotations[l.name]=str
            if all([chk.revealed for chk in l.checks]):
                colors[l.name] = 'green'
            elif any([chk.revealed for chk in l.checks]):
                colors[l.name] = 'orange'
            else:
                colors[l.name] = 'blue'
            if l.name == self.player.location:
                color_player[l.name] = 'blue'
            else: color_player[l.name] = 'white'

        IG = netgraph.InteractiveGraph(self.graph, node_labels=True, node_label_fontdict=dict(size=10,fontweight='bold'),
                                    node_layout=coords,
                                    node_size=5000, node_label_offset=100, edge_width=1000,
                                    node_shape = 'o', node_edge_color=colors, node_color=color_player,node_edge_width=1000,
                                    annotations=annotations, annotation_fontdict = dict(fontsize=8))
        plt.ioff()
        plt.show()

    def __deepcopy__(self,memodict={}):
        new = Game()
        new.locations = copy.deepcopy(self.locations)
        new.graph = networkx.Graph();
        for l in new.locations:
            new.graph.add_node(l.name,location=l)
        for l in new.locations:
            for (loc,steps) in l.steps_to.items():
                new.graph.add_edge(l.name,loc,steps=steps)
        new.player = copy.deepcopy(self.player)
        return new

def create(count=1,seed=None,verbose=False):
    if seed==None:
        # not actually random enough, but should be fine
        seed = numpy.random.randint(2**63)
        if verbose:
            print(f'no seed given, using seed {seed}')
    rng = numpy.random.default_rng(seed)

    randos = []
    locs = randomizer.read_json()
    for i in range(count):
        locations = copy.deepcopy(locs)
        randomizer.randomize(locations,rng,verbose)
        rando = Game(locations)
        if count==1: return rando
        randos.append(rando)
    return randos

# returns a possible game state that is consistent with a series of observations
#   observations is a list of (check,item) tuples
def create_from_observations(observations,player,count=1,seed=None,verbose=False):
    if seed==None:
        # not actually random enough, but should be fine
        seed = numpy.random.randint(2**63)
        if verbose:
            print(f'no seed given, using seed {seed}')
    rng = numpy.random.default_rng(seed)

    randos = []
    locs = randomizer.read_json()
    for i in range(count):
        locations = copy.deepcopy(locs)
        randomizer.randomize_remaining(locations,observations,rng,verbose)
        rando = Game(locations)
        rando.player = copy.deepcopy(player)
        if count==1: return rando
        randos.append(rando)
    return randos

def copy_with_observations(currGame, observations, count=1, verbose=False):
    randos = create_from_observations(observations, count=count, verbose=verbose)
    for rando in randos:
        copy_game_state(rando, currGame)
    return randos

def copy_game_state(newGame, oldGame):
        newGame.time = oldGame.time

        newGame.player.level = oldGame.player.level;
        newGame.player.exp = oldGame.player.exp;
        newGame.player.location = oldGame.player.location;
        newGame.player.key_items = oldGame.player.key_items;
        newGame.player.completed_checks = oldGame.player.completed_checks ;
        newGame.player.visited_locations = oldGame.player.visited_locations;

        for l in oldGame.graph.nodes:
            newGame.graph[l]['location'].visited = oldGame.graph[l]['location'].visited;
            newGame.graph[l]['location'].battles = oldGame.graph[l]['location'].battles;

            for chk in oldGame.graph[l]['location'].checks:
                newGame.graph[l]['location'].checks[chk].revealed = chk.revealed


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
