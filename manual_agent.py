#!/usr/bin/python
import game
#from randomizer import Item,Hm,Badge,Rule
if __name__=='__main__':

    #import pickle
    #observations = pickle.load( open('obsv.p','rb'))
    #observations_orig = pickle.load( open('obsv.p','rb'))
    #rando_record = game.create_from_observations(observations[:-5],verbose=True)
    #quit()


    rando = game.create()
    observations = [];
    
    while not rando.is_finished():
        while True:
            action_num = 1;
            actions = [];
            print(f'Player is at {rando.player.location}')
            print('Possible checks here are:')
            checks_here = rando.get_checks_here()
            if len(checks_here)==0: print('None')
            else:
                for chk in checks_here:
                    print(f'{action_num}: {chk}')
                    action_num+=1;
                    actions.append(chk)
            print('\n Connecting locations are:')
            neighbor_locs = rando.get_neighboring_locations()
            if len(neighbor_locs)==0: print('None')
            else:
                for loc in neighbor_locs:
                    print(f'{action_num}: {loc}')
                    action_num+=1;
                    actions.append(loc)

            print('\n Choose an action or 0 to print player info:')
            userinput = input()
            if userinput.isnumeric():
                choice = int(userinput)
            else: continue
            if choice == 0:
                print(f'Player level: {rando.player.level}')
                print(f'Player exp: {rando.player.exp:.0f}')
                print(f'Player items: {[item.name for item in rando.player.key_items if isinstance(item,game.randomizer.Item)]}')
                print(f'Player badges: {[badge.name for badge in rando.player.key_items if isinstance(badge,game.randomizer.Badge)]}')
                print(f'Player HMs: {[hm.name for hm in rando.player.key_items if isinstance(hm,game.randomizer.Hm)]}')
                print(f'    completed checks : {rando.player.completed_checks}')
                print(f'    all possible checks: {rando.get_accessible_checks()}\n')
                rando_record = game.create_from_observations(observations,verbose=True)
                rando_record.plot()
            if choice >0 and choice <=len(actions): break
        results,cost = rando.attempt_action(actions[choice-1])
        
        if game.is_location(results):
            print(f'Moved to {results}')
        elif results == None:
            print(f'Failed to achieve {actions[choice-1]}')
        else:
            for result in results:
                observations.append((actions[choice-1],result))
                print(f'Obtained {result}!')

        print(f'Cumulative Time: {rando.time}\n')

    games = game.create_from_observations(observations,verbose=True,count=100)
