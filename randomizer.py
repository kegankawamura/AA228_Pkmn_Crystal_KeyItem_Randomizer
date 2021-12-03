#!/usr/bin/python
import json
import numpy
import networkx
import matplotlib.pyplot as plt
import os
from enum import Enum,auto
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
    CANUSEFLY           = auto()
    CANUSESURF          = auto()
    CANUSEWHIRLPOOL     = auto()
    CANUSESTRENGTH      = auto()
    CANUSEWATERFALL     = auto()
    CANUSEFLASH         = auto()
    CANFIGHTTEAMROCKET  = auto()
    HAVEEIGHTBADGES     = auto()
    POWERPLANTMANAGER   = auto()
    TALKJASMINE         = auto()
    TALKBLUE            = auto()
    TALKMISTY           = auto()
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
    BEATRED             = auto()

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
    # returns approximate probability of successfully moving to this location
    def prob_success(self,player):
        prob = 1
        for battle in self.battles:
            prob *= battle.prob_success(player)
        return prob;
    def attempt(self,player):
        cost = self.cost(player);
        if(len(self.battles)):
            for battle in self.battles:
                # if already beaten trainer
                if battle.beat: continue;
                # if fail battle
                if not battle.battle(player):
                    return (False,cost+25)
        return (True,cost)

    def cost(self,player):
        return sum([b.cost() for b in self.battles if not b.beat]);

    def unrevealed_checks(self):
        return [chk for chk in self.checks if not chk.revealed]

    def __str__(self):
        return self.name ;
    def __repr__(self): return 'l: '+self.__str__()
    def __deepcopy__(self,memodict={}):
        new = Location()
        new.name = self.name;
        new.checks = copy.deepcopy(self.checks)
        new.rules = self.rules;
        new.coord = self.coord;
        new.visited = self.visited;
        new.battles = copy.deepcopy(self.battles);
        new.steps_to = self.steps_to;
        new.fly_point = self.fly_point;
        return new
    # equality across different games, lazy but should work
    def __eq__(self,other):
        return self.name == other.name;

class Check:
    def __init__(self):
        self.action = '';
        self.location = '';
        self.rules = [];
        self.steps = 0;
        self.battles = [];
        self.item_count = 0;
        self.item = [];
        self.revealed = False;
    # returns the approximate probability of success
    def prob_success(self,player):
        prob = 1
        for battle in self.battles:
            if battle.beat: continue;
            prob *= battle.prob_success(player)
        return prob;
    # returns item (None if fail) and time cost
    def attempt(self,player):
        cost = self.cost(player);
        if(len(self.battles)):
            for battle in self.battles:
                # if already beaten trainer
                if battle.beat: continue;
                # if fail battle
                if not battle.battle(player):
                    return (None,cost+25)
        # success
        self.revealed = True;
        for item in self.item:
            player.get_item(item)
        player.completed_checks.append(self)
        return (self.item,cost)
    # sum of cost to go (steps) and battle time
    def cost(self,player):
        return self.steps/player.speed() + sum([b.cost() for b in self.battles if not b.beat]);
    # equality across different games
    def __hash__(self):
        return hash(self.action)+hash(self.location)
    def __eq__(self,other):
        return hash(self)==hash(other)
    def __str__(self):
        return self.action;
    def __repr__(self):
        return 'ck: ' + self.__str__();
    def __deepcopy__(self,memodict={}):
        new = Check();
        new.action = self.action;
        new.location = self.location;
        new.rules = self.rules;
        new.steps = self.steps;
        new.battles = copy.deepcopy(self.battles);
        new.item_count = self.item_count;
        new.item = list(self.item);
        new.revealed = self.revealed;
        return new

class Battle:
    def __init__(self):
        # list of pokemon (levels)
        self.pokemon = [];
        self.beat = False;

    # using B/W exp curve , with some cheating
    def calculate_exp(self,player_level):
        a=1.5 # trainer constant
        b=137 # median base experience yield
        return numpy.sum([ a*b*poke/5 *
            ( (4*poke-5)/(poke+player_level-5) )**2.5 +1
                for poke in self.pokemon])
        #return numpy.sum([ a*b*poke/5 *
        #    ( (2*poke+10)/(poke+player_level+10) )**2.5 +1
        #        for poke in self.pokemon])
    # returns approximate probability of success
    def prob_success(self,player):
        prob = 1;
        l = player.level;
        for poke in self.pokemon:
            prob_win = Battle.interp_prob_win(l,poke)
            prob *= prob_win
        return prob
    # returns true if player beats this battle, and gives the player experience
    # returns false if player loses
    def battle(self,player):
        q = 20;
        l = player.level;
        for poke in self.pokemon:
            # these are just made up to be:
            #   20% chance to win against 4 pokes, 60% lower level
            #   80% '   ', match level
            #   95% '   ', 25% higher level
            # making it slightly easier to beat red
            prob_win = Battle.interp_prob_win(l,poke)
            if numpy.random.random_sample()>prob_win:
                # lose against poke
                return False;
        player.gain_exp(self.calculate_exp(l));
        self.beat = True;
        return True;
    # cost is assumed to be 30 sec per pokemon
    def cost(self):
        return 30*len(self.pokemon)
    def __deepcopy__(self,memodict={}):
        new = Battle()
        new.pokemon = self.pokemon
        new.beat = self.beat
        return new
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
    def interp_prob_win(player_level,poke):
        if poke > 75:
            interp_levels = [.3*poke,.9*poke,1.15*poke,1.2*poke]
        else:
            interp_levels = [.4*poke,poke,1.25*poke,1.3*poke]
        interp_prob_win = [.8,.95,.98,.999]
        prob_win = numpy.interp(player_level,interp_levels,interp_prob_win)
        return prob_win

#class WildBattle(Battle):
#    def calculate_exp(self,player_level):
#        return .75*super().calculate_exp(player_level)
#    def prob_success(self,player):



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
                rule.append(Rule.TALKMISTY)
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
                rule.append(Rule.BEATRED)
            else:
                raise Exception(f'rule {str} unknown')
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
    if num_badges >=14:
        rules.append(Rule.HAVEALLBADGES)
    if num_badges >=8:
        rules.append(Rule.HAVEEIGHTBADGES)
    if Hm.CUT in helditems and Badge.HIVE in helditems:
        rules.append(Rule.CANUSECUT)
    if Hm.FLY in helditems and Badge.STORM in helditems:
        rules.append(Rule.CANUSEFLY)
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

def progress_rules(helditems,logic,is_player=False):
    rules = [];
    if not is_player:
        rules.append(Rule.ROCKETWELL)
    itemset = set(helditems)
    logicset = set(logic).union(itemset)

    ecruteak = logicset.issuperset({Item.SQUIRTBOTTLE}) or\
                        logicset.issuperset({Item.PASS,Item.SSTICKET})
    saffron = logicset.issuperset({Item.PASS}) or\
                       logicset.issuperset({Item.SQUIRTBOTTLE,Item.SSTICKET})
    if is_player:
        snorlax = Rule.SNORLAX in helditems
    else:
        snorlax = saffron and logicset.issuperset({Item.POKEGEAR,Item.RADIOCARD,Item.EXPANSIONCARD})
    if snorlax: rules.append(Rule.SNORLAX); logicset.add(Rule.SNORLAX)
    viridian = logicset.issuperset({Rule.SNORLAX,Rule.CANUSECUT}) or\
                logicset.issuperset({Rule.CANUSESURF,Rule.CANUSEWATERFALL,Rule.HAVEEIGHTBADGES})

    if ecruteak: rules.append(ImpTown.ECRUTEAK)
    if saffron: rules.append(ImpTown.SAFFRON)
    if viridian: rules.append(ImpTown.VIRIDIAN)

    if not is_player:
        if saffron and ( logicset.issuperset({Rule.CANUSECUT,Rule.CANUSESURF}) or logicset.issuperset({Rule.CANUSEFLASH,Rule.CANUSESURF}) ):
            rules.append(Rule.POWERPLANTMANAGER)
            rules.append(Rule.TALKMISTY)
            if Item.MACHINEPART in itemset:
                rules.append(Rule.FIXPOWERPLANT)

        if ecruteak:
            rules.append(Rule.TALKJASMINE)
            if Item.SECRETPOTION in logicset:
                rules.append(Rule.RETURNPOTION)
            if logicset.issuperset({Rule.CANUSESURF,Rule.CANUSESTRENGTH}):
                rules.append(Rule.CHUCK)
            if Rule.CANUSESURF in logicset:
                rules.append(Rule.REDGYARADOS)
                rules.append(Rule.ELECTRODE)

        if viridian:
            if Rule.CANUSESURF in logicset:
                rules.append(Rule.TALKBLUE)
            #if logicset.issuperset({Item.POKEGEAR,Item.RADIOCARD,Item.EXPANSIONCARD}):
        if logicset.issuperset({Rule.HAVEEIGHTBADGES,Rule.CANUSESURF,Rule.CANUSEWATERFALL}) or logicset.issuperset({Rule.SNORLAX,Rule.CANUSECUT}):
            rules.append(Rule.ELITEFOUR)

        if Rule.HAVEALLBADGES in logicset:
            rules.append(Rule.OAK)


    return rules

def in_logic(helditems,is_player=False):
    logic_r = logical_rules(helditems)
    progress_r = progress_rules(helditems,logic_r,is_player)
    logic = set( (*helditems,*logic_r,*progress_r) ) # things 'inlogic'
    if is_player:
        logic.add(Rule.CANUSEFLASH)

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

def accessible_checks(locations, helditems,is_player=False):
    logic = in_logic(helditems,is_player)
    acc_checks = []
    set_blocks = set()


    for loc in locations:
        if is_reachable(loc,logic):
            for chk in loc.checks:
                if is_reachable(chk,logic) \
                        and not chk.revealed:
                    acc_checks.append(chk)
                else:
                    blocks = get_missing_rules(chk,logic)
                    for block in blocks:
                        # if a check is blocked by city progression, pass
                        if sum(isinstance(x,ImpTown) for x in block):
                            pass
                        elif len(block)>=1:
                            set_blocks = set_blocks.union(block)
        else:
            blocks = get_missing_rules(loc,logic)
            for block in blocks:
                if sum(isinstance(x,ImpTown) for x in block):
                    pass
                elif len(block)>=1:
                    set_blocks = set_blocks.union(block)
    return (acc_checks, set_blocks)

def accessible_locations(locations, helditems,is_player=False):
    logic = in_logic(helditems,is_player)
    acc_locs = []
    set_blocks = set()


    for loc in locations:
        if is_reachable(loc,logic):
            acc_locs.append(loc.name)
    return acc_locs

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
        if rule == Rule.TALKMISTY:
            items = get_items_from_rule(ImpTown.SAFFRON).union(
                    get_items_from_rule(Rule.POWERPLANTMANAGER))
            return items
        raise Exception(f'rule {rule} does not have a mapping to items')
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
            if 'battles' in js[0].keys():
                loc.battles = Battle.battle_from_list(js[0]['battles'])
            for check in js[0]['sections']:
                if valid_check(check):
                    chk = Check()
                    chk.location = loc.name
                    chk.action = check['name']
                    chk.steps = check['steps']
                    if 'battles' in check.keys():
                        chk.battles = Battle.battle_from_list(check['battles']);
                    if 'access_rules' in check.keys():
                        chk.rules = convert_rule(check['access_rules'])
                    if 'item_count' in check.keys():
                        chk.item_count = check['item_count'];
                    elif 'hosted_item' in check.keys():
                        if check['name']=='Gym - Chuck':
                            chk.item_count =2;
                            chk.item = convert_rule([check['hosted_item']])[0]
                        elif check['name'].find('Gym')>=0:
                            chk.item_count = 1;
                        elif check['name'].find('Red Gyarados')>=0 or check['name'].find('Electrodes')>=0:
                            chk.item_count = 2;
                            chk.item = convert_rule([check['hosted_item']])[0]
                        elif check['name']=='Red':
                            chk.item_count = 1;
                            chk.item = convert_rule([check['hosted_item']])[0]
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

def randomize(locations,rng=None,verbose=False):

    def reset_locations():
        for loc in locations:
            for chk in loc.checks:
                items = chk.item
                for item in items:
                    if item in items_accessible:
                        chk.item.remove(item)

    if rng==None:
        rng = numpy.random.default_rng()

    item_pool = set(Item).union(set(Hm)).union(set(Badge))
    items_accessible = []
    prev_acc_checks = []

    count = 0;
    cangetoutofGR = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.PASS in items_accessible
    cangetoutofSF = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.SSTICKET in items_accessible

    # ok im unbelivably dumb
    set_to_list  = lambda S : sorted(list(S),key=lambda i:i.name)
    choice_set  = lambda S : rng.choice(set_to_list(S))

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
        elif count==8 and Hm.FLY not in items_accessible: # make fly within early-mid checks
            rand_item = Hm.FLY
        elif  count == 9 and not cangetoutofGR(): # make sure SB / Pass are placed before leaving GR
            rand_item = rng.choice([Item.SQUIRTBOTTLE,Item.PASS])
        elif count == 12 and not cangetoutofSF(): # make sure SB / Ticket are placed before leaving SF
            rand_item = rng.choice([Item.SQUIRTBOTTLE,Item.SSTICKET])
        elif count==13 and Badge.STORM not in items_accessible:
            rand_item = Badge.STORM
        elif count > 15 and not get_items_from_rule(Rule.CANUSESURF).issubset(items_accessible):
            if Hm.SURF not in items_accessible: rand_item = Hm.SURF
            elif Badge.FOG not in items_accessible: rand_item = Badge.FOG
        else:
            # get random blocking item that hasnt been placed yet
            #rand_block = rng.choice(list(blocks))
            rand_block = choice_set(blocks)
            possible_items = get_items_from_rule(rand_block)
            #rand_item = rng.choice(list(possible_items))
            rand_item = choice_set(possible_items)
            try_count = 0;
            while rand_item not in item_pool:
                #rand_block = rng.choice(list(blocks))
                rand_block = choice_set(blocks)
                possible_items = get_items_from_rule(rand_block)
                #rand_item = rng.choice(list(possible_items))
                rand_item = choice_set(possible_items)
                try_count+=1
                if try_count >=200:
                    print(f'having trouble with {blocks} given these items: {items_accessible}')
                    reset_locations()
                    return randomize(locations,rng,verbose)


        # get random check that isnt filled already
        #weighted_checks = [*set_to_list(set(acc_checks)-set(prev_acc_checks)),*acc_checks]
        weighted_checks = [chk for chk in acc_checks if chk not in prev_acc_checks]+acc_checks
        while True:
            # make new checks twice as likely to be selected
            rand_check = rng.choice(weighted_checks)
            if len(rand_check.item)<rand_check.item_count:
                break;
            try_count+=1
            if try_count >=200:
                print(f'having trouble with {blocks} given these items: {items_accessible} and these checks: {acc_checks}')
                reset_locations()
                return randomize(locations,rng,verbose)
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
            acc_checks, _ = accessible_checks(locations,items_accessible)
            #rand_item = rng.choice(list(item_pool))
            rand_item = choice_set(item_pool)
            rand_check = rng.choice(acc_checks)
            while len(rand_check.item)>=rand_check.item_count:
                rand_check = rng.choice(acc_checks)
            # place item in check, and update sets of items
            rand_check.item.append(rand_item)
            items_accessible.append(rand_item)
            item_pool.remove(rand_item)
            if verbose:
                print(f'putting {rand_item.name} at check {rand_check}')

    count_trash = 0
    for ck in [ck for l in locations for ck in l.checks]:
        if ck.item_count > len(ck.item):
            ck.item.extend([rng.choice(list(Trash)) for i in range(ck.item_count-len(ck.item))])
            count_trash +=1
    return locations

# returns a randomized set of locations such that the set of observations is consistent
#   observations is a list of (check,item) tuples
def randomize_remaining(locations,obs_orig,rng=None,verbose=False):
    def reset_locations():
        for loc in locations:
            for chk in loc.checks:
                items = chk.item
                for item in items:
                    if item in items_accessible:
                        chk.item.remove(item)

    if rng==None:
        rng = numpy.random.default_rng()

    if len(obs_orig)>0:
        num_trash = sum([isinstance(x,Trash) for x in list(zip(*obs_orig))[1]])
    else:
        num_trash = 0
    observations = copy.copy(obs_orig)
    item_pool = set(Item).union(set(Hm)).union(set(Badge))
    items_accessible = []
    prev_acc_checks = []

    count = 0;
    cangetoutofGR = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.PASS in items_accessible
    cangetoutofSF = lambda : Item.SQUIRTBOTTLE in items_accessible or Item.SSTICKET in items_accessible

    # ok im unbelivably dumb
    set_to_list  = lambda S : sorted(list(S),key=lambda i:i.name)
    choice_set  = lambda S : rng.choice(set_to_list(S))

    acc_checks, blocks = accessible_checks(locations,items_accessible)

    def process_observations():
        count = 0
        added_observations = False
        for o_c,o_i in list(observations):
            if o_c in acc_checks:
                chk = next(c for c in acc_checks if c==o_c)
                observations.remove((o_c,o_i))
                #chk.revealed=True
                if o_i == Trash.TRASH:
                    chk.item.append(o_i)
                if o_i in item_pool:
                    chk.item.append(o_i)
                    if o_i == Trash.TRASH: continue;
                    items_accessible.append(o_i)
                    item_pool.remove(o_i)
                    count += 1
                    added_observations = True
                    if verbose:
                        print(f'observed {o_i.name} at check {o_c}')
        return added_observations,count


    blocked = True
    while len(item_pool)>0:
        try_count = 0;

        if blocked:
            acc_checks, blocks = accessible_checks(locations,items_accessible)
            if len(blocks)==0:
                blocked = False;
                break
        if len(observations)>0:
            added_observations,num_obs = process_observations()
            count += num_obs

        if count>=0-num_trash and Item.BICYCLE not in items_accessible : # first item is bicycle to ensure early bike
            prev_acc_checks = acc_checks
            rand_item = Item.BICYCLE
        elif count>=8-num_trash and Hm.FLY not in items_accessible and (len(observations)>0 and Hm.FLY not in list(zip(*observations))[1]): # make fly within early-mid checks
            rand_item = Hm.FLY
        elif  count >= 9-num_trash and not cangetoutofGR(): # make sure SB / Pass are placed before leaving GR
            rand_item = rng.choice([Item.SQUIRTBOTTLE,Item.PASS])
        elif count >= 12-num_trash and not cangetoutofSF(): # make sure SB / Ticket are placed before leaving SF
            rand_item = rng.choice([Item.SQUIRTBOTTLE,Item.SSTICKET])
        elif count>=13-num_trash and Badge.STORM not in items_accessible and (len(observations)>0 and Badge.STORM not in list(zip(*observations))[1]):
            rand_item = Badge.STORM
        elif count >= 15-num_trash and not get_items_from_rule(Rule.CANUSESURF).issubset(items_accessible):
            if Hm.SURF not in items_accessible: rand_item = Hm.SURF
            elif Badge.FOG not in items_accessible: rand_item = Badge.FOG
        else:
            # get random blocking item that hasnt been placed yet
            rand_block = choice_set(blocks)
            possible_items = get_items_from_rule(rand_block)
            rand_item = choice_set(possible_items)
            try_count = 0;
            while rand_item not in item_pool or ( len(observations) and rand_item in list(zip(*observations))[1] ) :
                rand_block = choice_set(blocks)
                possible_items = get_items_from_rule(rand_block).intersection(item_pool)
                try_count+=1
                if try_count >= 150:
                    process_observations()
                    acc_checks, blocks = accessible_checks(locations,items_accessible)
                    if len(blocks)==0:
                        #print('not actually blocked \\facepalm')
                        blocked = False; break;
                if try_count >=200:
                    print(f'having trouble with {blocks} given these items: {items_accessible}')
                    print('randomizer failed')
                    #return None
                    reset_locations()
                    return randomize_remaining(locations,obs_orig,rng,verbose)
                if len(possible_items)==0: continue
                rand_item = choice_set(possible_items)
            if not blocked: break;

        try_count = 0
        # get random check that isnt filled already
        weighted_checks = [chk for chk in acc_checks if chk not in prev_acc_checks]+acc_checks
        while True:
            # make new checks twice as likely to be selected
            rand_check = rng.choice(weighted_checks)
            if len(rand_check.item)<rand_check.item_count and ( len(observations)==0 or rand_check not in list(zip(*observations))[0] ) :
                break;
            try_count+=1
            if try_count >=150:
                acc_checks, blocks = accessible_checks(locations,items_accessible)
                weighted_checks = acc_checks
                if len(observations)>0:
                    added_observations,num_obs = process_observations()
                    weighted_checks, blocks = accessible_checks(locations,items_accessible)
                    acc_checks = weighted_checks
                    # try something smart for once
                    if len(observations)>0:
                        weighted_checks = [chk for chk in weighted_checks if chk not in list(zip(*observations))[1] and len(chk.item)<chk.item_count]
                        if len(weighted_checks)==0:
                            print('lol dont know how to even deal with this')
                            print('restarting randomizer')
                            reset_locations()
                            return randomize_remaining(locations,obs_orig,rng,verbose)
                    else:
                        weighted_checks = [chk for chk in weighted_checks if len(chk.item)<chk.item_count]
                    count += num_obs
                # get random blocking item that hasnt been placed yet
                while rand_item not in item_pool or ( len(observations) and rand_item in list(zip(*observations))[1] ) :
                    if len(blocks)==0:
                        #print('not actually blocked \\facepalm')
                        blocked = False; break;
                    rand_block = choice_set(blocks)
                    possible_items = get_items_from_rule(rand_block).intersection(item_pool)
                    try_count+=1
                    if try_count == 250 or try_count == 260: # might need to restart twice
                        process_observations()
                        acc_checks, blocks = accessible_checks(locations,items_accessible)
                        if len(blocks)==0:
                            #print('not actually blocked \\facepalm')
                            blocked = False; break;
                    if try_count >=300:
                        print(f'having trouble with {blocks} given these items: {items_accessible}')
                        print('restarting randomizer')
                        reset_locations()
                        return randomize_remaining(locations,obs_orig,rng,verbose)
                    if len(possible_items)==0: continue
                    rand_item = choice_set(possible_items)

                #print('not actually  something dumb?')
            if try_count >=500:
                print(f'having trouble with {blocks} given these items: {items_accessible} and these checks: {acc_checks}')
                print('restarting randomizer')
                reset_locations()
                return randomize_remaining(locations,obs_orig,rng,verbose)
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
            acc_checks, _ = accessible_checks(locations,items_accessible)
            rand_item = choice_set(item_pool)
            rand_check = rng.choice(acc_checks)
            while len(rand_check.item)>=rand_check.item_count:
                rand_check = rng.choice(acc_checks)
            # place item in check, and update sets of items
            rand_check.item.append(rand_item)
            items_accessible.append(rand_item)
            item_pool.remove(rand_item)
            if verbose:
                print(f'putting {rand_item.name} at check {rand_check}')

    count_trash = 0
    for ck in [ck for l in locations for ck in l.checks]:
        if ck.item_count > len(ck.item):
            ck.item.extend([rng.choice(list(Trash)) for i in range(ck.item_count-len(ck.item))])
            count_trash +=1

    if len(obs_orig):
        for loc in locations :
            for chk in loc.checks:
                if chk in list(zip(*obs_orig))[0]:
                    chk.revealed=True

    return locations

if __name__=='__main__':
    import game
    rando = game.create()
    #randos = run(1000)
    rando.player.key_items.append(Hm.FLY)
    rando.player.key_items.append(Badge.STORM)
    rando.player.visited_locations.add('Goldenrod City')
    rando.get_neighboring_locations()
