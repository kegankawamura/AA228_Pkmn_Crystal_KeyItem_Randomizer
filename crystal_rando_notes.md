# Pokemon Crystal Key Item Randomizer Logic Notes

## Resources
[randomizer](https://github.com/erudnick-cohen/Pokemon-Crystal-Item-Randomizer)

[tracker](https://github.com/vicendithas/pokemon-crystal-randomizer-tracker)

Tracker in Tricky/Extreme kir, so no visibility set

[image](https://imgur.com/a/dL5N1qv)

[map](https://i.pinimg.com/originals/e8/36/29/e83629e972aea6cf5450a8fc16f4875a.png)

[gsc scale map](https://i.redd.it/g5s6qtwml0f41.png)

[johto scale map](https://zyga.feen.us/z4rfb7z2jl.png)

[kanto scale map](https://zyga.feen.us/pujlb7q79q.png)

[scale map source](https://forums.pokemmo.eu/index.php?/topic/98250-11-scale-maps-for-the-regions/)

[exp calc](https://www.serebii.net/games/exp.shtml)

## Rules
Playing by [Extreme Key Item Rando rules](https://github.com/erudnick-cohen/Pokemon-Crystal-Item-Randomizer/blob/master/Modes/ExtremeKeyItemRando.yml):

* Key items, HMs, Pokegear+cards, and badges are randomized in a single pool among potential checks
* Items and hidden items are randomized in another pool 
* Pokemon locations and movesets are randomized
* Trainer Pokemon are randomized but keep the same levels

* Certain backtracking parts in the original are removed
* Bike is guaranteed to be at or before Goldenrod
* The cut tree in Ilex is removed, so cut is not required to get to Goldenrod
* Easy Tin Tower: Tin Tower is open if have clear bell, beat Morty, etc
* Elite 4 does not need to be beat to unlock Red

Goal is to beat Red 

Unlocking Red:

* all 16 badges
* radio card, expansion card, pokegear (wake up snorlax in front of diglett cave)
* 2 of 3: Magnet Pass, SS Aqua ticket, squirtbottle (Johto and Kanto progression)
* cut OR waterfall


## Badges and HMs

#### Johto Badges

Violet City (Falkner) - Zephyr, HM05 Flash

Azalea (Bugsy) - Hive, HM01 Cut

Goldenrod (Whitney) - Plain, HM04 Strength

Ecruteak (Morty) - Fog, HM03 Surf

Cianwood (Chuck) - Storm, HM02 Fly

Olivine (Jasmine) - Mineral

Mahogany (Pryce) - Glacier, HM06 Waterfall

Blackthorn (Clair) - Rising, HM07 Whirlpool 

  * Easy Clair means only gym is required to get the check

#### Kanto Badges

Pewter (Brock) - Boulder

Cerulean (Misty) - Cascade

Vermilion (Surge) - Thunder Badge

Celadon (Erika) - Rainbow

Fuchsia (Janine) - Soul

Saffron (Sabrina) - Marsh

Cinnabar (Blaine) - Volcano

Viridian (Blue) - Earth

## Team Rocket

Beating Team Rocket is required to beat the game (Im pretty sure)

1st encounter is beating slowpoke well, unlocks Bugsy

After Gyarados in Lake of Rage,
2nd encounter is Rocket Hideout in Mahogany, unlocks Pryce?

After having 7 badges [$canFightTeamRocket],
3rd encounter is the rocket takeover of Goldenrod Radio Tower:

  * False Director, Goldenrod Radio Tower
  * Rescue real Director, Goldenrod Underground Basement, requires basement key
  * Defeat Team Rocket, Goldenrod Radio Tower, requires card key


## Standard Checks and Key Items

Based on the tracker image

#### Row 1:

Pokegear - Mom New Bark Town

  * Make calls, not much by itself

Radio Card - Goldenrod Radio Tower quiz

  * Play radio if have Pokegear

Expansion Card - Lavender Radio Tower

  * Plays pokeflute with Pokegear and Radio Card, wake up snorlax

Squirtbottle - Goldenrod Flower Shop

  * Can remove Sudowoodo blocking Goldenrod-Violet-Ecruteak

Secret Potion - Cianwood Apothecary

  * Give to Jasmine in Lighthouse to unlock gym

    * Note that standard order is go up lighthouse to unlock apothecary, go to apothecary, return to lighthouse, but not necessary if already have secret potion
Card Key - Real Director in Underground

  * Unlock top of Radio tower to defeat Team Rocket

    * Note that standard order is go up radio tower to get basement key, go to basement to get card key, and beat rockets. If have card key, can skip buncha battles

SS Ticket - Given by Oak after beating E4

  * Travel between Olivine and Vermilion

(Magnet) Pass - Copycat girl Saffron

  * Travel between Goldenrod and Saffron

#### Row 2:

Machine Part - Cerulean Gym

  * Fixes Powerplant 

Clear Bell - Defeat Team Rocket in Radio Tower

  * Battle Suicune in Tin Tower; unlocks burned tower and rainbow wing check in rando

Rainbow Wing - we'll say burned tower

  * Battle Ho-oh at top of Tin Tower (useless)

Silver Wing - Pewter City Old Man 

  * Battle Lugia in Whirl Islands (useless)

Basement Key - Fake Director Goldenrod Radio Tower

  * Unlocks Basement door in underground

Lost Item - Pokefan club in Vermilion

  * Give to copycat girl in Saffron

Red Scale - Red Gyarados in Lake of Rage

  * trade for exp share (useless)

Mystery Egg - Mr Pokemon

  * get togepi (useless)

Water Stone - buy

  * trade for rock smash TM08 (useless)

#### Row 3:

Pokedex - Elm in New Bark Town

  * tracks seen pokemon (useless)

Bicycle - Bike shop in Goldenrod

  * zoom

Blue Card - Blue on Cinnabar

  * unlocks Blue's gym

Coin Case - Underground

  * Lets you gamble (useless)

Itemfinder - Ecruteak House

  * Helps finds hidden items (useless)

Old Rod - Route 32 Fisher

  * Catch low level pokemon

Good Rod - Olivine Fisher

  * Catch medium level pokes

Super Rod - Route 12 Fisher

  * Catch high level pokes



#### Row 4:

HMs have badge requirements

HM01 - Ilex Forest after rescuing Farfetchd

  * Cut trees

HM02 - Chuck's Wife Cianwood

  * Fly between previously visited cities + certain locations

HM03 - Kimono Girls Ecruteak

  * Surf over water

HM04 - Olivine Bar

  * Strength to move heavy rocks

HM05 - Beat Sprout Tower

  * Flash lights up dark caves

    * Flash is considered required by logic to go through Rock Tunnel and Silver Cave, but players usually skip this and break logic

HM06 - Rocket Hideout in Mahogany

  * Whirlpool to go through whirlpools (usually useless)

HM07 - Ice Path

  * Waterfall to travel up and down waterfalls

TM08 - Trade Water Stone to guy outside Violet

  * Rocksmash to break breakable rocks (useless)

#### Row 5:

Johto Badges in order

Zephyr, Hive, Plain, Fog, Storm, Mineral, Glacier, Rising

#### Row 6:

Kanto Badges in order

Boulder, Cascade, Thunder, Rainbow, Sould, Marsh, Volcano, Earth

#### Row 7:

Progression Checks 

Defeat Rocket, Beat Elite 4, Beat Red, Go mode, Have all 16 badges



## routes/locations and battles
#### maybe not all trainer battles are listed

T is a required trainer battle, numbers are the levels of their pokes


30 - T(2,4)

Sprout Tower (Violet) - T(3,3,3), T(6), T(6), T(7,7,10)

Violet Gym - T(9), T(7,7), T(7,9)

Slowpoke Well (Azalea) - T(9,9), T(9,11), T(7,9,9), T(14)

Azalea Gym - T(10,10), T(13), T(14,14,16)

Azalea Rival - T(12,14,16)

Underground (Goldenrod) - T(10)

Goldenrod Gym - T(18), T(18,20)

Sudowoodo - (20)

Burned Tower (Ecruteak) - T(20,20,18,22)

Ecruteak Gym - T(16,16,16,16,16), T(22), T(18,20,20), T(21,21,23,25)

Kimono Girls - T(17), T(17), T(17), T(17), T(17)

39 -T(17)

Radio Tower Team Rocket (Goldenrod) - T(24,24), T(26), T(26,26), T(23,23,25), T(24,26)

  after card key: T(36), T(32,32, 32), T(33, 33)



False Director - T(30,30,30,30,32,30)

  can skip 3 trainers with card key

T(25), T(23,23,25), T(22,23,22,21)??

Rescue Director - T(7,9), T(30,30,32,32,28)

  more battles if not complete radio tower team rocket

Gyarados (Lake of Rage) - 30

Rocket Hideout (Mahogany) -  T(17,19), T(16,17,18), T(20,20,20), T(18,18), T(18,18), T(19), T(22,22,24), T(23,23,25), (23)x3

Mahogany Gym - T(28), T(27,29,31)

Blackthorn Gym - T(34,34,34), T(37), T(34,36), T(34,36), T(37,37,40,37)

Saffron Gym - T(46,46,48)

10 - T(35)

Fuchsia Gym - T(36,36,36,33,39)

Lighthouse (Olivine) - T(20), T(18,18), T(21)

Olivine Gym - T(30,30,35)

Cianwood Gym - T(27), T(27), T(25,25), T(23,23,25), T(27,30)

Vermilion Gym - T(37,33), T(44,40,40,46,40)

Snorlax (Vermillion) - (50)

Pewter Gym - T(37), T(41,41,42,44,42)

Cinnabar Gym - T(45,50,,45)

Viridian Gym - T(56,54,56,58,58,58)

Nugget Bridge - T(35), T(30,34), T(33,33), T(28,31,31), T(34), T(29,32,29), T(36)

Cerulean Gym - T(42,44,47,42)

Erica - T(35,35), T(37), T(32,32,35), T(42,41,46,46)

Elite 4 - T(40,41,41,41,42), T(40,41,43,42,44), T(42,42,42,43,46), T(42,42,45,44,47), T(44,47,47,46,46,50)

Tin Tower - T(32,32), T(32,32), T(32,32), 40

Red - T(81,73,75,77,77,77)

