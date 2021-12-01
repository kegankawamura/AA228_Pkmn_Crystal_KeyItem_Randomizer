#!/usr/bin/python
import game
import dm.mcts as mcts

#from randomizer import Item,Hm,Badge,Rule
if __name__=='__main__':

    #import pickle
    #observations = pickle.load( open('obsv.p','rb'))
    #observations_orig = pickle.load( open('obsv.p','rb'))
    #rando_record = game.create_from_observations(observations[:-5],verbose=True)
    #quit()


    rando = game.create()
    observations = [];
    dm_model = mcts.MCTS(rando, 1, numParticles=50)


    history_action = []
    history_turns = []

    verbose = False

    while not rando.is_finished():
        try:
            if verbose:
                print(f'Player level: {rando.player.level}')
                print(f'Player exp: {rando.player.exp:.0f}')
                print(f'Player items: {[item.name for item in rando.player.key_items if isinstance(item,game.randomizer.Item)]}')
                print(f'Player badges: {[badge.name for badge in rando.player.key_items if isinstance(badge,game.randomizer.Badge)]}')
                print(f'Player HMs: {[hm.name for hm in rando.player.key_items if isinstance(hm,game.randomizer.Hm)]}')
                print(f'    completed checks : {rando.player.completed_checks}')
                print(f'    all possible checks: {rando.get_accessible_checks()}\n')


            actions = [];

            if verbose:
                print(f'Player is at {rando.player.location}')
                print('Possible checks here are:')

            checks_here = rando.get_checks_here()
            if verbose and len(checks_here)==0:
                print('None')
            else:
                for chk in checks_here:
                    if verbose: print(f'{chk}')
                    actions.append(chk)
            if verbose: print('\n Connecting locations are:')
            neighbor_locs = rando.get_neighboring_locations()
            if len(neighbor_locs)==0: print('None')
            else:
                for loc in neighbor_locs:
                    if verbose: print(f'{loc}')
                    actions.append(loc)

            a_idx = dm_model.chooseAction(actions, m = 10)

            history_action.append((rando.player.location, actions[a_idx]))
            history_turns.append(rando.time)

            results,cost = rando.attempt_action(actions[a_idx])

            if game.is_location(results):
                if verbose: print(f'Moved to {results}')
            elif results == None:
                if verbose: print(f'Failed to achieve {actions[a_idx]}')
            else:
                for result in results:
                    observations.append((actions[a_idx],result))
                    dm_model.addObservation((actions[a_idx],result))
                    if verbose: print(f'Obtained {result}!')


            print(f'Cumulative Time: {rando.time}\n')
        except KeyboardInterrupt:
            break


    with open('pkmnHistoryData_mcts.txt', 'w') as f:
        print("writing to data file")
        f.write(f'{rando.time}\n')
        for i in range(len(history_turns)):
            f.write(f"{history_action[i]}, {history_turns[i]}\n")
        f.write(f"{dm_model._Q}")
