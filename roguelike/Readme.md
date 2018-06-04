# Simple Roguelike

## How to run the game
You need to create instanse of Game and call method 'run':
```
game = Game()
game.run
```

## Little description
You just got bored so you went for a walk in the dungeon.
There are inhabitants that want to taste you or drink your blood.
You are not such a simple guy so decide to counterattack. _Kill them all!_

## Game objects
#### You:
Symbol: **@**<br/>

Initial characteristics:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*health* = **100**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*defense* = **1**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*power* = **2**<br/>

Initial equipment:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*dagger* (in the main hand)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Symbol: **-**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Gives **2** points to the power<br/>


You can keep 26 items in the inventory.


#### Your enemies:
Killing enemies gives you experience points so you can improve your skills.

- **spiders**<br/>
Symbol: **x**<br/>
Characteristics:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*health* = **20**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*defense* = **0**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*power* = **4**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*experience* = **35**<br/>
- **bats**<br/>
Symbol: **V**<br/>
Characteristics:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*health* = **25**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*defense* = **1**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*power* = **6**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*experience* = **50**<br/>
- **snakes**<br/>
Symbol: **S**<br/>
Characteristics:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*health* = **30**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*defense* = **2**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*power* = **8**<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*experience* = **70**<br/>

#### Bonuses:
- **healing potion**<br/>
Symbol: **+**<br/>
Gives **40** points to the health<br/>
- **sword**<br/>
Symbol: **T**<br/>
Gives **4** points to the power<br/>
- **shield**<br/>
Symbol: **O**<br/>
Gives **2** points to the defence<br/>

#### Stairs
Symbol: **>**<br/>
The stairs to the lower floor of the dungeon.

## Control
- _up_, _u_ - move up
- _down_, _j_ - move down
- _right_, _k_ - move right
- _left_, _h_ - move left
- _y_, _i_, _n_, _m_ - move diagonally
- _q_ - show control
- _w_ - skip your move
- _s_ - pickup an item
- _d_ - go downstairs
- _a_ - show an inventory
- _x_ - drop an inventory
- _c_ - show hero information
