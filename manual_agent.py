#!/usr/bin/python
import game
#from randomizer import Item,Hm,Badge,Rule
if __name__=='__main__':
    rando = game.create()
    
    while not rando.is_finished():
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
        while True:
            print('\n Choose an action or 0 to print player info:')
            userinput = input()
            if userinput.isnumeric():
                choice = int(userinput)
            else: continue
            if choice == 0:
                print(f'Player level: {rando.player.level}')
                print(f'Player exp: {rando.player.exp}')
                print(f'Player items: {rando.player.key_items}')
                print(f'completed checks : {rando.player.completed_checks}')
                print(f'all possible checks: {rando.get_accessible_checks()}')
            if choice >0 and choice <=len(actions): break
        results,cost = rando.attempt_action(actions[choice-1])
        
        if game.is_location(results):
            print(f'Moved to {results}')
        elif results == None:
            print(f'Failed to achieve {actions[choice-1]}')
        else:
            for result in results:
                print(f'Obtained {result}!')

        print(f'Cumulative Time: {rando.time}\n')
