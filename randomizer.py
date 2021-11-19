#!/usr/bin/python
import json
import numpy
import networkx
import matplotlib.pyplot as plt
import os
from enum import Enum,auto
import random
import pdb
import netgraph
import copy

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class Item(AutoName):
    SQUIRTBOTTLE        = auto()
    PASS                = auto()
    SSTICKET            = auto()
    CARDKEY             = auto()
    BASEMENTKEY         = auto()
    SECRETPOTION        = auto()
    MACHINEPART         = auto()
    BICYCLE             = auto()
    CLEARBELL           = auto()
    POKEGEAR            = auto()
    RADIOCARD           = auto()
    EXPANSIONCARD       = auto()
    LOSTITEM            = auto()

class Trash(AutoName):
    TRASH               = auto()

class Badge(AutoName):
    ZEPHYR              = auto() # Flash
    HIVE                = auto() # Cut
    PLAIN               = auto() # Strength
    FOG                 = auto() # Surf
    STORM               = auto() # Fly
    MINERAL             = auto()
    GLACIER             = auto() # Waterfall
    RISING              = auto() # Whirlpool
    BOULDER             = auto()
    CASCADE             = auto()
    THUNDER             = auto()
    RAINBOW             = auto()
    SOUL                = auto()
    MARSH               = auto()
    VOLCANO             = auto()
    EARTH               = auto()

class Hm(Enum):
    CUT         = 1
    FLY         = 2
    SURF        = 3 
    STRENGTH    = 4
    FLASH       = 5
    WATERFALL   = 6
    WHIRLPOOL   = 7

class Rule(AutoName):
    CANUSECUT           = auto()
    CANUSESURF          = auto()
    CANUSEWHIRLPOOL     = auto()
    CANUSESTRENGTH      = auto() 
    CANUSEWATERFALL     = auto()
    CANUSEFLASH         = auto()
    CANFIGHTTEAMROCKET  = auto()
    HAVEEIGHTBADGES     = auto()
    POWERPLANTMANAGER   = auto()
    #TALKMISTY           = auto()
    TALKJASMINE         = auto()
    TALKBLUE            = auto()
    CHUCK               = auto()
    SNORLAX             = auto()
    ROCKETWELL          = auto()
    FIXPOWERPLANT       = auto()
    REDGYARADOS         = auto()
    ELECTRODE           = auto()
    OAK                 = auto()
    ELITEFOUR           = auto()
    RETURNPOTION        = auto()
    HAVEALLBADGES       = auto()

class ImpTown(Enum):
    SAFFRON     = 'Saffron City'
    ECRUTEAK    = 'Ecruteak City'
    VIRIDIAN    = 'Viridian City'

class Location:
    def __init__(self):
        # collection of checks 
        self.name = '';
        self.checks = [];
        self.rules = [];
        self.coord = ();
        self.visited = False;
        self.battles = [];
        self.steps_to = {};
        self.fly_point = False;

    def is_accessible(self,items):
        return
    def __str__(self):
        return self.name ;
    def __repr__(self): return 'l: '+self.__str__()
    
class Route:
    # path from Location to location
    def __init__(self):
        self.number = 0;
        self.endpoints = [];
        self.cost = [];
        self.battles = [];
    def __str__(self):
        return str(self.number) + ' between '+ self.endpoints[0] + ' and '+self.endpoints[1];
    def __repr__(self):
        return 'r: ' + self.__str__();

class Check:
    def __init__(self):
        self.action = '';
        self.rules = [];
        self.steps = [];
        self.battles = [];
        self.item_count = 0;
        self.item = [];
        self.revealed = False;
    def __str__(self):
        return self.action;
    def __repr__(self):
        return 'ck: ' + self.__str__();

class Battle:
    def __init__(self):
        # list of pokemon (levels)
        self.pokemon = [];
        self.beat = False;

    def calculate_exp(self):
        a = 1.5; b = 3; c = 2;
        return numpy.cumsum([a*b*c*poke for poke in self.pokemon])
    # returns true if player beats this battle, and gives the player experience
    # returns false if player loses
    def battle(self,player):
        q = 20;
        l = player.level;
        for poke in self.pokemon:
            adv = (q*l/(poke + q*l))**3 # squiggly line
            if numpy.random.random_sample()>adv:
                # lose against poke
                return false;
        player.gain_exp(self.calculate_exp());
        self.beat = True;
        return True;

    def __str__(self):
        return str(self.pokemon);
    def __repr__(self):
        return 'b: ' + self.__str__();
    def battle_from_list(b_list):
        battles = [];
        for b in b_list:
            battle = Battle();
            battle.pokemon = b;
            battles.append(battle)
        return battles


class Player:
    def __init__():
        self.level = 5;
        self.exp = 0;
        self.location = "";
        self.key_items = [];
        self.completed_checks = [];

    def gain_exp(self,exp):
        if self.level>=100: return
        self.exp += exp;
        lvl_up_exp = level_exp(self.level+1)-level_exp(self.level)
        if self.exp >= lvl_up_exp:
            self.level+=1
            self.exp %= lvl_up_exp
        return
    def level_exp(level):
        return level**3;

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
        return

    # get possible checks for the player that have not been visited 
    # realize this is not so useful since checks dont have obvious
    # correspondence to locations
    def get_next_checks(self):
        items = self.player.key_items
        return accessible_checks(self.locations,items)


    def plot(self):
        locations = self.locations
        coords = dict(zip([l.name for l in locations],[l.coord for l in locations]))
        labels = dict(zip([l.name for l in locations],[l.name for l in locations]))
        annotations = dict()
        for l in locations:
            str = ''
            for chk in l.checks:
                if chk.item_count>0:
                    str+= chk.action + ' : ' + chk.item[-1].name + '\n'
            annotations[l.name]=str
        
        IG = netgraph.InteractiveGraph(self.graph, node_labels=True, node_label_fontdict=dict(size=10,fontweight='bold'),
                                    node_layout=coords, 
                                    node_size=5000, node_label_offset=100, edge_width=1000, 
                                    node_shape = 'o', node_edge_color='blue', node_edge_width=1000,
                                    annotations=annotations, annotation_fontdict = dict(fontsize=8))
        plt.show()

def convert_rule(jrule):
    rule_list = [];
    for jstr in jrule:
        rulestr_list = [x.strip() for x in jstr.split(',')]
        rule = [];
        for str in rulestr_list:
            if   str == '@canUseCut':
                rule.append(Rule.CANUSECUT)
            elif str == '@canUseSurf':
                rule.append(Rule.CANUSESURF)
            elif str == '@canUseStrength':
                rule.append(Rule.CANUSESTRENGTH)
            elif str.find('@canUseFlash')>=0:
                rule.append(Rule.CANUSEFLASH)
            elif str == '@canUseWaterfall':
                rule.append(Rule.CANUSEWATERFALL)
            elif str == '@canUseWhirlpool':
                rule.append(Rule.CANUSEWHIRLPOOL)
            elif str == 'snorlax':
                rule.append(Rule.SNORLAX)
            elif str == '$haveEightBadges':
                rule.append(Rule.HAVEEIGHTBADGES)
            elif str == '$canFightTeamRocket':
                rule.append(Rule.CANFIGHTTEAMROCKET)
            elif str == 'power_plant_manager':
                rule.append(Rule.POWERPLANTMANAGER)
            elif str == 'talk_jasmine':
                rule.append(Rule.TALKJASMINE)
            elif str == 'talk_blue':
                rule.append(Rule.TALKBLUE)
            elif str == 'chuck':
                rule.append(Rule.CHUCK)
            elif str == '$haveEnoughBadges':
                rule.append(Rule.HAVEALLBADGES)
            elif str == 'fix_power_plant':
                rule.append(Rule.FIXPOWERPLANT)
            elif str == 'rocketgrunt':
                rule.append(Rule.ROCKETWELL)
            elif str == 'red_gyarados':
                rule.append(Rule.REDGYARADOS)
            elif str == 'electrode':
                rule.append(Rule.ELECTRODE)
            elif str == 'oak':
                rule.append(Rule.OAK)

            elif str == 'squirt_bottle':
                rule.append(Item.SQUIRTBOTTLE)
            elif str == 'pass':
                rule.append(Item.PASS)
            elif str == 'ss_ticket':
                rule.append(Item.SSTICKET)
            elif str == 'card_key':
                rule.append(Item.CARDKEY)
            elif str == 'basement_key':
                rule.append(Item.BASEMENTKEY)
            elif str == 'secret_potion':
                rule.append(Item.SECRETPOTION)
            elif str == 'machine_part':
                rule.append(Item.MACHINEPART)
            elif str == 'bicycle':
                rule.append(Item.BICYCLE)
            elif str == 'clear_bell':
                rule.append(Item.CLEARBELL)
            elif str == 'pokegear':
                rule.append(Item.POKEGEAR)
            elif str == 'radio_card':
                rule.append(Item.RADIOCARD)
            elif str == 'expansion_card':
                rule.append(Item.EXPANSIONCARD)
            elif str == 'lost_item':
                rule.append(Item.LOSTITEM)
            elif str == 'plain_badge':
                rule.append(Badge.PLAIN)

            elif str == '@Saffron City':
                rule.append(ImpTown.SAFFRON)
            elif str == '@Ecruteak City':
                rule.append(ImpTown.ECRUTEAK)
            elif str == '@Viridian City':
                rule.append(ImpTown.VIRIDIAN)

            elif str == 'team_rocket':
                pass
            elif str == 'elite_four':
                rule.append(Rule.ELITEFOUR)

                pass
            elif str == '$noCutTree':
                pass
            elif str == 'talk_misty':
                pass
            elif str == 'open_silver':
                pass
            elif str == '$noEliteFour':
                pass
            elif str == 'return_potion':
               rule.append(Rule.RETURNPOTION)
            elif str == '[backward_kanto]':
                pass
            elif str == "farfetch'd":
                pass
            elif str == "red":
                pass
            else:
                import pdb; pdb.set_trace()
        rule_list.append(rule)
    return rule_list;

def find_location(locations, name):
    idx = [l.name.find(name)>=0 for l in locations]
    arr = numpy.array(locations)[idx]
    if len(arr)==0: return None
    return arr[0]

def logical_rules(helditems):
    rules = []
    num_badges =  sum(isinstance(x,Badge) for x in helditems)
    if num_badges >=7:
        rules.append(Rule.CANFIGHTTEAMROCKET)
    if num_badges >=16:
        rules.append(Rule.HAVEALLBADGES)
    if num_badges >=8:
        rules.append(Rule.HAVEEIGHTBADGES)
    if Hm.CUT in helditems and Badge.HIVE in helditems:
        rules.append(Rule.CANUSECUT)
    if Hm.SURF in helditems and Badge.FOG in helditems:
        rules.append(Rule.CANUSESURF)
    if Hm.STRENGTH in helditems and Badge.PLAIN in helditems:
        rules.append(Rule.CANUSESTRENGTH)
    if Hm.FLASH in helditems and Badge.ZEPHYR in helditems:
        rules.append(Rule.CANUSEFLASH)
    if Hm.WHIRLPOOL in helditems and Badge.GLACIER in helditems:
        rules.append(Rule.CANUSEWHIRLPOOL)
    if Hm.WATERFALL in helditems and Badge.RISING in helditems:
        rules.append(Rule.CANUSEWATERFALL)
    return rules

def progress_rules(helditems,logic):
    rules = [];
    rules.append(Rule.ROCKETWELL)
    itemset = set(helditems)
    logicset = set(logic).union(itemset)

    ecruteak = lambda : logicset.issuperset({Item.SQUIRTBOTTLE}) or\
                        logicset.issuperset({Item.PASS,Item.SSTICKET})
    saffron = lambda : logicset.issuperset({Item.PASS}) or\
                       logicset.issuperset({Item.SQUIRTBOTTLE,Item.SSTICKET})
    snorlax = lambda : saffron() and logicset.issuperset({Item.POKEGEAR,Item.RADIOCARD,Item.EXPANSIONCARD})
    if snorlax(): rules.append(Rule.SNORLAX); logicset.add(Rule.SNORLAX)
    viridian = lambda : logicset.issuperset({Rule.SNORLAX,Rule.CANUSECUT}) or\
                       logicset.issuperset({Rule.CANUSESURF,Rule.CANUSEWATERFALL,Rule.HAVEEIGHTBADGES})


    if ecruteak(): rules.append(ImpTown.ECRUTEAK)
    if saffron(): rules.append(ImpTown.SAFFRON)
    if viridian(): rules.append(ImpTown.VIRIDIAN)
    
    if saffron() and ( logicset.issuperset({Rule.CANUSECUT,Rule.CANUSESURF}) or logicset.issuperset({Rule.CANUSEFLASH,Rule.CANUSESURF}) ):
        rules.append(Rule.POWERPLANTMANAGER)
        if Item.MACHINEPART in itemset:
            rules.append(Rule.FIXPOWERPLANT)

    if ecruteak():
        rules.append(Rule.TALKJASMINE)
        if Item.SECRETPOTION in logicset:
            rules.append(Rule.RETURNPOTION)
        if logicset.issuperset({Rule.CANUSESURF,Rule.CANUSESTRENGTH}):
            rules.append(Rule.CHUCK)
        if Rule.CANUSESURF in logicset:
            rules.append(Rule.REDGYARADOS)
            rules.append(Rule.ELECTRODE)

    if viridian():
        if Rule.CANUSESURF in logicset:
            rules.append(Rule.TALKBLUE)
        #if logicset.issuperset({Item.POKEGEAR,Item.RADIOCARD,Item.EXPANSIONCARD}):
    if logicset.issuperset({Rule.HAVEEIGHTBADGES,Rule.CANUSESURF,Rule.CANUSEWATERFALL}) or logicset.issuperset({Rule.SNORLAX,Rule.CANUSECUT}):
        rules.append(Rule.ELITEFOUR)

    if Rule.HAVEALLBADGES in logicset:
        rules.append(Rule.OAK)


    return rules

def in_logic(helditems):
    logic_r = logical_rules(helditems)
    progress_r = progress_rules(helditems,logic_r)
    logic = set( (*helditems,*logic_r,*progress_r) ) # things 'inlogic'
    return logic

def is_reachable(place,set_access):
    if len(place.rules)==0: return True;
    for r in place.rules:
        set_rule = set(r)
        if set_access.issuperset(set_rule):
            return True
    return False

def get_missing_rules(place,set_access):
    missing = [];
    for r in place.rules:
        set_rule = set(r)
        missing.append(set_rule.difference(set_access))
    return missing

def accessible_checks(locations, helditems):
    logic = in_logic(helditems)
    acc_checks = []
    set_blocks = set()

    
    for loc in locations:
        if is_reachable(loc,logic):
            for chk in loc.checks:
                if is_reachable(chk,logic) and not chk.revealed:
                    acc_checks.append(chk)
                else:
                    blocks = get_missing_rules(chk,logic)
                    for block in blocks:
                        # if a check is blocked by city progression, pass
                        if sum(isinstance(x,ImpTown) for x in block):
                            pass
                        elif len(block)>=1: 
                            if Rule.SNORLAX in block and Rule.SNORLAX in logic: pdb.set_trace()
                            set_blocks = set_blocks.union(block)
        else:
            blocks = get_missing_rules(loc,logic)
            for block in blocks:
                if sum(isinstance(x,ImpTown) for x in block):
                    pass
                elif len(block)>=1: 
                    set_blocks = set_blocks.union(block)
    return (acc_checks, set_blocks)

# converts [items,rules] to [items,badges,hms]
def get_items_from_rule(rule):
    items = set()
    if isinstance(rule,Item): items.add(rule); return items
    if isinstance(rule,Badge): items.add(rule); return items
    else:
        if rule == Rule.CANUSECUT:
            items.add(Hm.CUT); items.add(Badge.HIVE); return items
        if rule == Rule.CANUSESURF:
            items.add(Hm.SURF); items.add(Badge.FOG); return items
        if rule == Rule.CANUSESTRENGTH:
            items.add(Hm.STRENGTH); items.add(Badge.PLAIN); return items
        if rule == Rule.CANUSEFLASH:
            items.add(Hm.FLASH); items.add(Badge.ZEPHYR); return items
        if rule == Rule.CANUSEWHIRLPOOL:
            items.add(Hm.WHIRLPOOL); items.add(Badge.GLACIER); return items
        if rule == Rule.CANUSEWATERFALL:
            items.add(Hm.WATERFALL); items.add(Badge.RISING); return items
        if rule == Rule.CANFIGHTTEAMROCKET or rule == Rule.HAVEEIGHTBADGES or rule == Rule.HAVEALLBADGES or rule == Rule.OAK:
            items = items.union(Badge); return items
        if rule == Rule.FIXPOWERPLANT:
            items.add(Item.MACHINEPART); return items
        if rule == Rule.ELITEFOUR:
            items = items.union(Badge).union(
            get_items_from_rule(Rule.CANUSESURF)).union(
            get_items_from_rule(Rule.CANUSEWATERFALL)).union(
            get_items_from_rule(Rule.SNORLAX)).union(
            get_items_from_rule(Rule.CANUSECUT)) 
            return items
        if rule == ImpTown.ECRUTEAK:
            items = items.union({Item.PASS,Item.SQUIRTBOTTLE,Item.SSTICKET})
            return items
        if rule == ImpTown.SAFFRON:
            items = {Item.PASS,Item.SQUIRTBOTTLE,Item.SSTICKET}
            return items;
        if rule == ImpTown.VIRIDIAN:
            items = get_items_from_rule(Rule.SNORLAX).union(
                    get_items_from_rule(Rule.CANUSECUT)).union(
                    get_items_from_rule(Rule.CANUSESURF)).union(
                    get_items_from_rule(Rule.CANUSEWATERFALL)).union(
                    get_items_from_rule(Rule.HAVEEIGHTBADGES))
            return items;
        if rule == Rule.SNORLAX:
            items = items.union({Item.POKEGEAR,Item.RADIOCARD,Item.EXPANSIONCARD}).union({Item.PASS,Item.SQUIRTBOTTLE,Item.SSTICKET})
            return items
        if rule == Rule.REDGYARADOS or rule == Rule.ELECTRODE:
            items = items.union( get_items_from_rule(ImpTown.ECRUTEAK)).union(
                get_items_from_rule(Rule.CANUSESURF))
            return items
        if rule == Rule.RETURNPOTION:
            items = items.union(get_items_from_rule(ImpTown.ECRUTEAK))
            items.add(Item.SECRETPOTION)
            return items
        if rule == Rule.POWERPLANTMANAGER:
            items = get_items_from_rule(ImpTown.SAFFRON).union(
                    get_items_from_rule(Rule.CANUSESURF)).union(
                    get_items_from_rule(Rule.CANUSEFLASH)).union(
                    get_items_from_rule(Rule.CANUSECUT))
            return items
        if rule ==Rule.CHUCK:
            items = get_items_from_rule(ImpTown.ECRUTEAK).union(
                    get_items_from_rule(Rule.CANUSESURF)).union(
                    get_items_from_rule(Rule.CANUSESTRENGTH))
            return items
        if rule == Rule.TALKBLUE:
            items = get_items_from_rule(ImpTown.VIRIDIAN).union(
                    get_items_from_rule(Rule.CANUSESURF))
            return items

        pdb.set_trace()
    return items

def read_json():
    locations_path = 'pokemon-crystal-randomizer-tracker/locations/'
    locations = [];
    
    for filepath in sorted(os.scandir(locations_path),key=lambda fp: fp.name):
        if (not filepath.name.endswith(".json") or filepath.name.find('virtual')>=0):
            continue;
        #print(filepath.path)
        file = open(filepath.path)
        js = json.load(file)
        
        # structure of json:
        #           list of size 1 :
        #               dict with fields:
        #                   'name' - string name
        #                   'access_rules' - list of access rules (str)
        #                   'sections' - dict of checks at this location (dicts): 
        #                       'name' - string name
        #                       ## sections may or may not have the following keys
        #                       'access_rules' - list of access rules (str)
        #                       'visibility_rules' - list of settings to be available (str)
        #                   'map_locations' - dict of pixel location on map drawing:
        #                       'map'
        #                       'x'
        #                       'y'
        
        valid_check = lambda check: 'visibility_rules' not in check.keys() or check['visibility_rules'][0]=='tin_tower'
    
        valid_location = False;
        # get valid checks in extreme KIR
        for check in js[0]['sections']:
            if valid_check(check):
                valid_location = True;
                break
        
        if valid_location:
            loc = Location()
            loc.name = js[0]['name']
            coord = js[0]['map_locations'][0]
            loc.coord = (coord['x'],-coord['y'])
            if 'battles' in js[0].keys():
                loc.battles = Battle.battle_from_list(js[0]['battles']);
            if 'fly_point' in js[0].keys():
                loc.fly_point = True;
            if 'steps_to' in js[0].keys():
                loc.steps_to = js[0]['steps_to']
            if 'access_rules' in js[0].keys():
                loc.rules = convert_rule(js[0]['access_rules'])
            for check in js[0]['sections']:
                if valid_check(check):
                    chk = Check()
                    chk.action = check['name']
                    if 'battles' in check.keys():
                        loc.battles = Battle.battle_from_list(check['battles']);
                    if 'access_rules' in check.keys():
                        chk.rules = convert_rule(check['access_rules'])
                    if 'item_count' in check.keys():
                        chk.item_count = check['item_count'];
                    elif 'hosted_item' in check.keys():
                        if check['name'].find('Gym')>=0:
                            chk.item_count = 1;
                        elif check['name'].find('Speak To')>=0:
                            chk.item_count = 0;
                        elif check['name'].find('Red')>=0:
                            chk.item_count = 0;
                        else:
                            chk.item_count = 1;
                            chk.item = convert_rule([check['hosted_item']])[0]
    
                    loc.checks.append(chk)
            locations.append(loc)
    return locations

    # idea: maintain a graph and game state (available items, locations, and abilities)
    #       get set of limiting items (any that block a check)
    #       randomly sample limiting items and place in random available check 
    #       repeat until graph is complete (all checks are available)
    #       fill in rest of items
    
def randomize(locations,verbose=False):
    item_pool = set(Item).union(set(Hm)).union(set(Badge))
    items_accessible = []
    prev_acc_checks = []
    
    count = 0;
    #cangetoutofGR = lambda : Item.SQUIRTBOTTLE in items_accessible or set(Item.PASS,Item.SSTICKET).issubset(set(items_accessible))
    cangetoutofGR = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.PASS in items_accessible
    cangetoutofSF = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.SSTICKET in items_accessible
    
    blocked = True
    while len(item_pool)>0:
        try_count = 0;

        if blocked:
            acc_checks, blocks = accessible_checks(locations,items_accessible)
            if len(blocks)==0:
                blocked = False;
                break
    
        if count==0: # first item is bicycle to ensure early bike
            prev_acc_checks = acc_checks
            rand_item = Item.BICYCLE
        elif  count == 12 and not cangetoutofGR(): # make sure SB / Pass are placed before leaving GR
            rand_item = random.choice([Item.SQUIRTBOTTLE,Item.PASS])
            #pdb.set_trace()
        elif count == 15 and not cangetoutofSF(): # make sure SB / Ticket are placed before leaving SF
            rand_item = random.choice([Item.SQUIRTBOTTLE,Item.SSTICKET])
        elif count > 19 and not get_items_from_rule(Rule.CANUSESURF).issubset(items_accessible):
            if Hm.SURF not in items_accessible: rand_item = Hm.SURF
            elif Badge.FOG not in items_accessible: rand_item = Badge.FOG
        else:
            # get random blocking item that hasnt been placed yet 
            rand_block = random.choice(list(blocks))
            possible_items = get_items_from_rule(rand_block)
            rand_item = random.choice(list(possible_items))
            try_count = 0;
            while rand_item not in item_pool:
                rand_block = random.choice(list(blocks))
                possible_items = get_items_from_rule(rand_block)
                rand_item = random.choice(list(possible_items))
                try_count+=1
                if try_count >=200:
                    print(f'having trouble with {blocks} given these items: {items_accessible}')
                    pdb.set_trace()

    
        # get random check that isnt filled already
        weighted_checks = [*list(set(acc_checks)-set(prev_acc_checks)),*acc_checks]
        while True:
            # make new checks twice as likely to be selected
            rand_check = random.choice(weighted_checks)
            if len(rand_check.item)<rand_check.item_count:
                break;
            try_count+=1
            if try_count >=200:
                print(f'having trouble with {blocks} given these items: {items_accessible} and these checks: {acc_checks}')
                pdb.set_trace()
                randomize(locations,verbose)
        # place item in check, and update sets of items
        rand_check.item.append(rand_item)
        items_accessible.append(rand_item)
        item_pool.remove(rand_item)
        if verbose:
            print(f'putting {rand_item.name} at check {rand_check}')
        count +=1
        prev_acc_checks = acc_checks

    if len(item_pool)>0:
        while len(item_pool)>0:
            rand_item = random.choice(list(item_pool))
            rand_check = random.choice(acc_checks)
            while len(rand_check.item)>=rand_check.item_count:
                rand_check = random.choice(acc_checks)
            # place item in check, and update sets of items
            rand_check.item.append(rand_item)
            items_accessible.append(rand_item)
            item_pool.remove(rand_item)
            if verbose:
                print(f'putting {rand_item.name} at check {rand_check}')
    
    count_trash = 0
    for ck in [ck for l in locations for ck in l.checks]:
        if ck.item_count > len(ck.item):
            ck.item.extend([random.choice(list(Trash)) for i in range(ck.item_count-len(ck.item))])
            count_trash +=1
    return locations

def run(count=1,verbose=False):
    randos = []
    locs = read_json()
    for i in range(count):
        locations = copy.deepcopy(locs)
        randomize(locations,verbose)
        rando = Game(locations)
        if count==1: return rando
        randos.append(rando)
    #rando.plot()
    return randos

if __name__=='__main__':
    rando = run()
    #rando.plot()
    randos = run(1000)
