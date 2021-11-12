# Project Proposal

* problem that you would like to solve for your final project
* why you believe it is a decision-making problem
* sources of uncertainty

## Pokemon Crystal Key Item Randomizer

Pokemon Crystal Key Item Randomizer is a randomized variation of a typical Pokemon game where the goal is to complete the game as quickly as possible. Key items refer to a subset of items in Pokemon games, most of which are required to progress the story of the game. Key items are in set locations throughout the game, usually restricting the player to linear progression. As an example, beating a Pokemon gym gives the player the ability to surf, which opens access to the next city. In a key item randomizer, the locations of each key item, called checks, are kept the same, but the key items are randomly shuffled between locations, subject to certain logical constraints. This results in a highly non-linear game, where the player has to choose which checks to pursue based on the perceived difficulty, time investment, and possible utility of the random key item. For the final project, we would like to create a program that decides which checks to go after next based on the state of the game.

>> would need to explain checks and key items more, and like the actual game??

Uncertainty in Pokemon Crystal Key Item Randomizer primarily comes from the randomized locations of key items. However, key items are not simply distributed uniformly randomly throughout the game. Because checks and key items are randomized according to logical progression, inferencing is a powerful tool in the decision making process and will be a major focus of the decision making policy. For example, at the beginning of the game, the player has access to a limited number of checks and is completely blocked by a handful of key items. Observations of some of a particular check then influences the likelihood that the remaining are vital for the completion of the game. This randomization is the main source of uncertainty, but the base game also includes uncertainty surrounding checks.

>> could describe the comparative utility of certain checks???

At a broad level, the probability of successfully winning a Pokemon battle is conditioned on the particular Pokemon involved, their stats and levels, and their moves. Often the path to a particular check requires beating a number of opponents, so this probability distribution drives uncertainty in successfully attaining a check. For example, the beginning routes have fewer battles and at a lower level than those near the end of the game, so there is greater probability of getting to early game checks than late game checks. However, as the player progresses through the game and their Pokemon gain levels and experience, later battles get easier, potentially influencing the decision making policy. This extends to uncertainty in the cost of pursuing a check, as the time investment of reaching a check could be thought of as proportional to the difficulty of the battles involved.

>> simplify the problem more, e.g. time could be known while success is still variable??

We chose to focus on the problem of choosing what checks to pursue as this is at the core of Pokemon Crystal Key Item Randomizer. The probability of key items in checks is influenced by the already observed checks and knowledge about the logical structure of the randomization process. In addition, the potential utility of a check is weighed against its completion time and chance of success. We can also consider the player's Pokemon's level as a state, in which successfully beating opponents will award the player with experience and increase the odds of winning harder fights.


>> maybe set the overall goal to compare different decision making processes?
