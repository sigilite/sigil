
### Sigil Online

import sol_spells



# The only core game feature 
# not yet implemented is detecting that the game
# is going in a loop (after 5 repeats of the board state)
# and making blue win in this case (after giving red fair warning).
# But I'll save that for another time.




### FEATURES TO IMPLEMENT:

### 'reset' command that you can input into any prompt






class Node():
	def __init__(self, name):
		self.name = name

		### neighbors is a list of node objects which are adjacent
		self.neighbors = []

		### stone is None when empty, 'red' or 'blue' when filled
		self.stone = None




class Spell():

	def __init__(self, board, position, name):
		self.board = board

		### position is a list of the node objects
		### which constitute this spell.
		self.position = position


		self.name = name


		### True iff it's a charm
		self.ischarm = False



		### The 'charged' attribute will equal 'red' or 'blue'
		### if one of them has the spell fully charged, and None otherwise
		self.charged = None


		### Overwrite these in the actual spell classes.
		### Note that two_sigil_refill is just the EXTRA refill from
		### second sigil. (which you will ADD to the one_sigil_refill)
		self.one_sigil_refill = 0
		self.two_sigil_refill = 0


	def cast(self, player):
		### sacrifice all stones in it, and refill appropriate
		### number based on sigils
		pname = player.color[0].upper() + player.color[1:]
		print(pname + " casts " + self.name)
		if self.ischarm:
			for node in self.position:
				node.stone = None

		elif player.sigils == 3:
			pass

		else:
			for node in self.position:
				node.stone = None

			if player.sigils == 0:
				refills = 0

			elif player.sigils == 1:
				refills = self.one_sigil_refill

			elif player.sigils == 2:
				refills = self.one_sigil_refill + self.two_sigil_refill

			if refills > 1:
				print("You get to keep {} stones in ".format(refills) + self.name + ".")
			elif refills == 1:
				print("You get to keep 1 stone in " + self.name + ".")

			while refills > 0:
				keep = input("Select a stone to keep: ")
				if self.board.nodes[keep] not in self.position:
					print("That's not a node in your spell!")

				elif self.board.nodes[keep].stone != None:
					print("You already kept that stone!")
					continue
				else:
					refills -= 1
					self.board.nodes[keep].stone = player.color
		self.board.update()


		self.resolve(player)
		
		if not self.ischarm:
			player.lock = self
			self.board.countdown -= 1


	def resolve(self, player):
		### The actual effect!!! 
		### Overwrite this in the specific spell classes.
		pass




	def update_charge(self):
		### Sets the 'charged' attribute to correctly reflect
		### the current board state.  Must be called every time
		### the board state changes.

		firststone = self.position[0].stone
		if len(self.position) == 1:
			self.charged = firststone
			return None
		else:
			for node in self.position[1:]:
				if node.stone != firststone:
					self.charged = None
					return None
			self.charged = firststone





############################ These should be moved to a module

class Sprout(Spell):
	def __init__(self, board, position, name):
		super().__init__(board, position, name)
		self.ischarm = True

	def resolve(self, player):
		player.softmove()

class Grow(Spell):
	def __init__(self, board, position, name):
		super().__init__(board, position, name)
		self.one_sigil_refill = 0
		self.two_sigil_refill = 1

	def resolve(self, player):
		for i in range(3):
			player.softmove()

class Flourish(Spell):
	def __init__(self, board, position, name):
		super().__init__(board, position, name)
		self.one_sigil_refill = 1
		self.two_sigil_refill = 1

	def resolve(self, player):
		for i in range(4):
			player.softmove()

########################### These should be moved to a module










class Board():
	def __init__(self):
		### nodes is a dict that takes strings (names) 
		### and returns the corresponding node objects
		self.nodes = self.make_board()
		

		### positions is a dict with keys 1-9.  1,2,3 are major spells
		### in zones a,b,c respectively.  4,5,6 are minor spells.
		### 7,8,9 are charms.
		### Each value is a list of nodes, the ones
		### constituting that spell.
		self.positions = self.make_positions()


		### spells is a list of the 9 spell objects on the board.
		### These objects are defined by the spell class,
		### as well as the child class corresponding to
		### what spell it is.
		self.spells = self.make_spells()




		### spelldict is a dictionary with keys = spell names
		### (strings), and values which are the spell objects themselves.
		self.spelldict = self.make_spelldict()



		### There will also be board attributes for the two players.
		### But they will get added by the board.addplayers() method,
		### which we call AFTER constructing the board and then
		### constructing the players.

		### These will be player objects after the addplayers() method
		### is called.

		### ONLY REFER TO THESE ATTRIBUTES 
		### after the board setup has been finished!
		self.redplayer = None
		self.blueplayer = None


		### The spell countdown! The EOT trigger checks in
		### player.taketurn will check if board.countdown == 0,
		### and if so, end the game appropriately.
		self.countdown = 7






	def update(self):
		### Updates the status of all the spells.
		### These statuses will be stored
		### in the 'charged_spells' attributes of players.

		### Also updates the players' 'sigils' attributes.

		### board.update() MUST BE CALLED WHENEVER
		### ANY STONE CHANGES POSITION!

		redcharged = []
		bluecharged = []
		for spell in self.spells:
			spell.update_charge()
			if spell.charged == 'red':
				redcharged.append(spell)
			elif spell.charged == 'blue':
				bluecharged.append(spell)

		self.redplayer.charged_spells = redcharged
		self.blueplayer.charged_spells = bluecharged

		redsigils = 0
		bluesigils = 0

		for node in [self.nodes['a1'], self.nodes['b1'], self.nodes['c1']]:
			if node.stone == 'red':
				redsigils += 1
			elif node.stone == 'blue':
				bluesigils += 1

		self.redplayer.sigils = redsigils
		self.blueplayer.sigils = bluesigils






	def display(self, whoseturn):
		### Displays the current board state.
		### Gets called at the BEGINNING of each turn.
		redlist = []
		bluelist = []
		for name in self.nodes:
			color = self.nodes[name].stone
			if color == 'red':
				redlist.append(name)
			elif color == 'blue':
				bluelist.append(name)
		print("\n\n\nRed stones: ", redlist)
		print("Blue stones: ", bluelist)

		redtotal = len(redlist)
		bluetotal = len(bluelist) + 1
		if whoseturn == 'red':
			if bluetotal > redtotal:
				print("Blue is winning by " + str(bluetotal - redtotal))
			else:
				print("Red is winning by " + str(redtotal + 1 - bluetotal))

		elif whoseturn == 'blue':
			if redtotal > bluetotal:
				print("Red is winning by " + str(redtotal - bluetotal))
			else:
				print("Blue is winning by " + str(bluetotal + 1 - redtotal))





		print("Red Sigils: ", red.sigils)
		print("Blue Sigils: ", blue.sigils)
		if self.countdown > 1:
			print("{} spellcasts remaining".format(self.countdown))
		elif self.countdown == 1:
			print("1 spellcast remaining")




	def end_game(self, winner):
		### Right now this doesn't DO anything special,
		### just prints some silly stuff.
		### But this would be a good place to put any 'store the data'
		### type code.
		print("Game over-- the winner is " + winner.upper() + " !!!")
		for i in range(9):
			print(winner.upper() + " VICTORY")




	def make_board(self):
		nodelist = []
		
		for zone in ['a','b','c']:
			for number in range(1,14):
				x = Node(zone + str(number))
				nodelist.append(x)
		
		for i in range(len(nodelist)):
			node = nodelist[i]
			name = node.name
		
			if name[1:] == '1':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+10])
		
			elif name[1:] == '2':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+4])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '3':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+10])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '4':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+3])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '5':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+7])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '6':
				node.neighbors.append(nodelist[i+5])
				node.neighbors.append(nodelist[i-4])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '7':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i-3])
		
			elif name[1:] == '8':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+2])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '9':
				node.neighbors.append(nodelist[i+1])
				node.neighbors.append(nodelist[i+4])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '10':
				node.neighbors.append(nodelist[i-2])
				node.neighbors.append(nodelist[i-1])
		
			elif name[1:] == '11':
				node.neighbors.append(nodelist[i-10])
				node.neighbors.append(nodelist[i-5])
		
			elif name[1:] == '12':
				node.neighbors.append(nodelist[i-7])
		
			elif name[1:] == '13':
				node.neighbors.append(nodelist[i-10])
				node.neighbors.append(nodelist[i-4])
		
		interzone_edges = []
		interzone_edges.append((nodelist[10], nodelist[35]))
		interzone_edges.append((nodelist[11], nodelist[32]))
		interzone_edges.append((nodelist[6], nodelist[24]))
		interzone_edges.append((nodelist[9], nodelist[23]))
		interzone_edges.append((nodelist[19], nodelist[37]))
		interzone_edges.append((nodelist[22], nodelist[36]))
		
		for x in interzone_edges:
			left = x[0]
			right = x[1]
			left.neighbors.append(right)
			right.neighbors.append(left)

		nodedict = {}
		for node in nodelist:
			nodedict[node.name] = node

		return nodedict




	def make_positions(self):
		### Returns a dictionary d with with keys 1-9 and values = the 9
		### positions.  1,2,3 are major spells
		### in zones a,b,c respectively.  4,5,6 are minor spells.
		### 7,8,9 are charms.
		### Each of these position values is a list of nodes, the ones
		### constituting that spell.

		n = self.nodes
		d = {}
		d[1] = [n['a2'], n['a3'], n['a4'], n['a5'], n['a6']]
		d[2] = [n['b2'], n['b3'], n['b4'], n['b5'], n['b6']]
		d[3] = [n['c2'], n['c3'], n['c4'], n['c5'], n['c6']]
		d[4] = [n['a8'], n['a9'], n['a10']]
		d[5] = [n['b8'], n['b9'], n['b10']]
		d[6] = [n['c8'], n['c9'], n['c10']]
		d[7] = [n['a7']]
		d[8] = [n['b7']]
		d[9] = [n['c7']]

		return d



	def make_spells(self):
		### returns the list of spell objects that will be on the board

		### spellnames is just a list of strings which are the names
		### of the spells to be instantiated, in order of their
		### position, 1-9.
		spellnames = sol_spells.spell_list

		### Convert this spellnames list into a list of spell objects
		### and return that in-order list of spell objects
		
		spells = []

		for x in spellnames:
			nextspell = eval(x)
			spells.append(nextspell)

		for charm in spells[6:]:
			charm.ischarm = True
		

		return spells




	def make_spelldict(self):
		### Returns a dictionary which takes in names of spells
		### and returns the spell objects.

		d = {}
		for spell in self.spells:
			d[spell.name] = spell

		return d




	def addplayers(self, redplayer, blueplayer):
		### Call this method AFTER building the board and the players.
		### This is my hack-y way of giving players the board as parameter,
		### and also giving the board players as parameters.

		self.redplayer = redplayer
		self.blueplayer = blueplayer






class Player():
	### color parameter should be 'red' or 'blue'
	def __init__(self, board, color):
		self.board = board
		self.color = color
		if self.color == 'red':
			self.enemy = 'blue'
		else:
			self.enemy = 'red'

		### charged_spells is a list of which spell objects
		### are currently charged for this player.
		### Gets updated whenever board.update() is called.
		self.charged_spells = []

		### sigils is the number of sigils this player controls.
		### Gets updated by board.update()
		self.sigils = 0


		self.lock = None



	def taketurn(self, canmove = True, candash = True, cancharm = True, canspell = True):

		actions = []
		charmlist = []
		spelllist = []
		if canmove:
			actions.append('move')
		if candash:
			actions.append('dash')
		if cancharm:
			self.board.update()
			for spell in self.charged_spells:
				if spell.ischarm:
					actions.append(spell.name)
					charmlist.append(spell.name)
		if not canmove:
			if canspell:
				self.board.update()
				for spell in self.charged_spells:
					if not spell.ischarm and self.lock != spell:
						actions.append(spell.name)
						spelllist.append(spell.name)
			actions.append('pass')



		print("\nSelect an action:")
		print(actions)
		action = input()
		if action not in actions:
			print("Invalid action!")
			self.taketurn(canmove, candash, cancharm, canspell)
			return None

		if action == 'move':
			self.move()
			self.taketurn(False, candash, cancharm, canspell)
			return None

		elif action == 'dash':
			self.dash()
			self.taketurn(canmove, False, cancharm, canspell)
			return None

		elif action in charmlist:
			self.board.spelldict[action].cast(self)
			self.taketurn(canmove, candash, False, canspell)

		elif action in spelllist:
			self.board.spelldict[action].cast(self)
			self.taketurn(False, False, False, False)


		elif action == 'pass':
			return None





	def bot_triggers(self, whoseturn):
		### Put any spell-specific BOT triggers here,
		### like Inferno, which should set the global
		### variables gameover = True and winner = self.enemy
		pass


	def eot_triggers(self, whoseturn):
		### Put code in here for every specific spell
		### that causes eot triggers. 
		### It must come BEFORE the end-game code below!

		### Check whether someone is up by 3 or more.

		### Check whether the countdown == 0.
		global gameover
		global winner



		### INSERT SPELL-SPECIFIC EOT EFFECTS HERE




		redtotal = 0
		bluetotal = 1

		for name in self.board.nodes:
			color = self.board.nodes[name].stone
			if color == 'red':
				redtotal += 1
			elif color == 'blue':
				bluetotal += 1

		if redtotal > bluetotal + 2:
			gameover = True
			winner = 'red'

		elif bluetotal > redtotal + 2:
			gameover = True
			winner = 'blue'

		else:
			if self.board.countdown == 0:
				gameover = True
				if redtotal > bluetotal:
					winner = 'red'
				elif bluetotal > redtotal:
					winner = 'blue'
				else:
					a = ['red', 'blue']
					a.remove(whoseturn)
					winner = a[0]





	def firstmove(self):
		nodename = input("Where would you like to place your first stone? ")
		node = self.board.nodes[nodename]
		if node.stone != None:
			print("Invalid move-- your opponent started there!")
			self.firstmove()
			return None
		else:
			node.stone = self.color
			self.board.update()


	def move(self):
		nodename = input("Where would you like to move? ")
		node = self.board.nodes[nodename]
		adjacent = False
		for neighbor in node.neighbors:
			if neighbor.stone == self.color:
				adjacent = True

		if node.stone == self.color:
			print("Invalid move-- you already have a stone there!")
			self.move()
			return None

		elif not adjacent:
			print("Invalid move-- that's not adjacent to you!")
			self.move()
			return None

		elif node.stone == None:
			node.stone = self.color
			self.board.update()

		elif node.stone == self.enemy:
			self.pushenemy(node)


	def softmove(self):
		nodename = input("Where would you like to soft move? ")
		node = self.board.nodes[nodename]
		adjacent = False
		for neighbor in node.neighbors:
			if neighbor.stone == self.color:
				adjacent = True

		if node.stone == None and adjacent:
			node.stone = self.color

		elif node.stone == self.color:
			print("Invalid move-- you already have a stone there!")
			self.softmove()
			return None

		elif not adjacent:
			print("Invalid move-- that's not adjacent to you!")
			self.softmove()
			return None

		elif node.stone == self.enemy:
			print("Invalid move-- that's not a soft move!")
			self.softmove()
			return None


	def hardmove(self):
		nodename = input("Where would you like to hard move? ")
		node = self.board.nodes[nodename]
		adjacent = False
		for neighbor in node.neighbors:
			if neighbor.stone == self.color:
				adjacent = True

		if not adjacent:
			print("Invalid move-- that's not adjacent to you!")
			self.hardmove()
			return None

		elif node.stone == self.color:
			print("Invalid move-- you already have a stone there!")
			self.hardmove()
			return None

		elif node.stone != self.enemy:
			print("Invalid move-- that's not a hard move!")
			self.hardmove()
			return None

		else:
			self.pushenemy(node)

	def dash(self):
		sac1 = input("Select your first stone to sacrifice. ")
		if self.board.nodes[sac1].stone != self.color:
			print("You do not have a stone there!")
			self.dash()
			return None

		sac2 = input("Select your second stone to sacrifice. ")
		if (self.board.nodes[sac2].stone != self.color) or (sac2 == sac1):
			print("You do not have a stone there!")
			self.dash()
			return None

		self.board.nodes[sac1].stone = None
		self.board.nodes[sac2].stone = None
		self.board.update()
		self.move()
		



	def pushenemy(self, node):		
		node.stone = self.color
		### push the enemy stone. Return a list of options
		### for where to push it.
		pushingqueue = [(x, 1) for x in node.neighbors]
		pushingoptions = []
		alreadyvisited = [node]
		### This loop searches for a first valid pushing option
		while pushingoptions == []:
			if pushingqueue == []:
				print("Enemy stone crushed!")
				self.board.update()
				return None
			nextpair = pushingqueue.pop(0)
			nextnode, distance = nextpair
			alreadyvisited.append(nextnode)
			if nextnode.stone == self.color:
				continue
			elif nextnode.stone == self.enemy:
				for neighbor in nextnode.neighbors:
					if neighbor not in alreadyvisited:
						pushingqueue.append((neighbor, distance + 1))
				continue
			else:
				pushingoptions.append(nextnode)
				shortestdistance = distance

		### This loop finishes finding the other pushing options
		### at the same distance, and breaks when distance gets bigger
		while pushingqueue != []:
			nextpair = pushingqueue.pop(0)
			nextnode, distance = nextpair
			if distance > shortestdistance:
				break
			if nextnode.stone == None:
				pushingoptions.append(nextnode)

		pushingoptionnames = [x.name for x in pushingoptions]

		while True:
			print("\nThe enemy stone can be pushed to: ", pushingoptionnames)
			push = input("Where would you like to push it? ")
			if push not in pushingoptionnames:
				print("Invalid option!")
				continue
			self.board.nodes[push].stone = self.enemy
			self.board.update()
			print("Enemy stone pushed to " + push)
			break


			

##############  GAME LOOP  ##############			

		

### First we set up the objects.  This is my hack-y way of passing
### everyone as parameters to everyone else: doing it
### in two layers, using the board.addplayers method

board = Board()
red = Player(board, 'red')
blue = Player(board, 'blue')
board.addplayers(red, blue)



turncounter = 3
gameover = False
winner = None


print("\nRed Turn 1")
red.firstmove()

print("\nBlue Turn 1")
blue.firstmove()


while True:
	turncounter += 1

	if turncounter % 2 == 0:
		activeplayer = red
		whoseturn = 'red'
	else:
		activeplayer = blue
		whoseturn = 'blue'

	board.display(whoseturn)
	activeplayer.bot_triggers(whoseturn)
	if gameover:
		board.end_game(winner)
		break
		

	if whoseturn == 'red':
		print("\n\n\nRed Turn " + str(turncounter // 2))
		red.taketurn()
	else:
		print("\n\n\nBlue Turn " + str(turncounter // 2))
		blue.taketurn()


	activeplayer.eot_triggers(whoseturn)
	if gameover:
		board.end_game(winner)
		break








