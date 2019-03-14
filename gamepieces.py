# __TO DO LIST_____
# x change game board from list of objects to dictionary
# x triggers
# x create enemies (walking triggers)
# x create collectables
# . rewrite player advance (include function abstraction in place of dash)
# . implement buzz meter
# . decide on final specs (game screen size, player size, final controls)
# . animation in place of draw
# done with gamepeices.py

from __future__ import unicode_literals, print_function
import pygame
from pygame.locals import *
import sys, os
DEBUG = 'debug' in sys.argv

pygame.init()
FONT = pygame.font.SysFont("helvetica", 10)
CLOCK = pygame.time.Clock()

class GamePiece(pygame.rect.Rect):
	"Anything with the daunting task of being in the game"
	def __init__(self, *args, **kwargs):
		"""let args be rect arguments"""
		pygame.rect.Rect.__init__(self, *args)
		for key in kwargs:
			setattr(self, key, kwargs[key])

	def _debug(self):
		if not DEBUG: return
		print(self.__dict__)

	def draw(self, destination):
		#overwrite with animation 
		pygame.draw.rect(destination, self.color, self)
		destination.blit(FONT.render(self.name, 0, (0, 0, 0)),
		(self.x, self.y))

	def advance(self, game):
		if DEBUG: self._debug()
		pass #overwrite with cool functionality,
		# or just leave for static platform


class Player(GamePiece):
	def __init__(self, *args, **kwargs):
		GamePiece.__init__(self, *args, **kwargs)
		self.x_vel = 0
		self.y_vel = 0
		self.direction = 1 #pos = right, neg = left

		self.grav = kwargs["grav"]
		self.jump_vel = kwargs["jump_vel"]
		self.jumps = kwargs["jumps"]
		self.dash = kwargs["dash"]
		self.dash_speed = kwargs["dash_speed"]
		self.dash_frames = kwargs["dash_frames"]
		self.dash_counter = 0
		self.walk_speed = kwargs["walk_speed"]
		self.speed = kwargs["speed"]
		self.friction = kwargs["friction"]

		self.keys = pygame.key.get_pressed()
		self.buttons = {
			"left": K_LEFT,
			"right": K_RIGHT,
			"jump": K_z,
			"dash": K_x
		}
		self.collectables = []

	def _set_buttons(self, buttons):
		self.buttons = buttons

	def render_input(self):
		for event in pygame.event.get():
			if event.type == QUIT: quit() 
			if (event.type == KEYDOWN):
				if event.key == self.buttons['jump'] and self.jumps > 0:
					self.jumps -= 1
					self.y_vel = self.jump_vel
				if event.key == self.buttons['dash'] and self.dash:
					self.x_vel = self.dash_speed * self.direction
					self.dash = False
		self.keys = pygame.key.get_pressed()
		if self.dash_counter == 0 and self.keys[self.buttons['left']] != self.keys[self.buttons['right']]:
				self.direction = -1 if self.keys[self.buttons['left']] else 1
		self.x_vel = max(
			min(abs(self.x_vel) + (self.speed * (self.keys[self.buttons['right']] or self.keys[self.buttons['left']])), self.walk_speed),
			abs(self.x_vel)
		) * self.direction


	def advance(self, game):
		if DEBUG: GamePiece._debug(self)
		self.render_input()
		platforms = game["platforms"]
		collectables = game["collectables"]
		# Y update and hit detection
		self.y_vel += self.grav	

		i = self.move(0, self.y_vel).collidelist([plat for plat in platforms])
		if i != -1:			
			if self.y_vel > 0: 
				self.jumps = 2
				# velocity correction
				while self.y_vel and platforms[i].colliderect(pygame.rect.Rect(
					(self.left, self.bottom), (self.w, self.y_vel) )  ):
					self.y_vel -= 1
					if DEBUG: print("y velocity correction", self.y_vel)
			else: self.y_vel = 0
			if abs(self.x_vel) and self.dash:
				if (self.keys[self.buttons['right']] or self.keys[self.buttons['left']]):
					self.x_vel = max(abs(self.x_vel) - self.friction, self.walk_speed
						) * self.direction
				else:
					self.x_vel = max(abs(self.x_vel) - self.friction, 0
						) * self.direction

		# X update and hit detection
		if self.dash_counter:
			if self.dash_counter == self.dash_frames:
				self.dash_counter = 0

		i = self.move(self.x_vel, 0).collidelist([plat for plat in platforms])
		if i != -1:
			while platforms[i].colliderect(pygame.rect.Rect(
						*[
							((self.left + self.x_vel, self.top), (abs(self.x_vel), self.h)), "sneaky",
							((self.right, self.top), (abs(self.x_vel), self.h)) 
						][self.direction + 1])  ):
					self.x_vel -= self.direction
					if DEBUG: print("x velocity correction", self.x_vel)

		#cornerbug fix
		if self.move(self.x_vel, self.y_vel).collidelist(
			[plat for plat in platforms]) != -1:
			self.x_vel, self.y_vel = 0, 0

		if self.dash_counter == 0: self.dash = True
		else: 
			self.y_vel = 0
			self.x_vel = self.dash_speed


		self.move_ip(self.x_vel, self.y_vel)

		i = self.collidelist(collectables)
		if i != -1:
			self.collectables.append(collectables[i].name)
			game["collectables"].pop(i)


		

class Trigger(GamePiece):
	"""important note, in this engine, triggers look for hit detection with player 
	while player looks for hit detection with tangibles"""
	def __init__(self, *args, **kwargs):
		GamePiece.__init__(self, *args, **kwargs)
		self.function = kwargs['trigger_function']
		self.triggered = False

	def draw(self, destination):
		if not DEBUG: return
		GamePiece.draw(self, destination)

	def advance(self, game):
		if DEBUG: GamePiece._debug(self)
		if not self.triggered and self.colliderect(game["player"]):
			self.triggered = True
			self.function(self, game)
		#doesnt turn itself back on, function should do that


class Enemy(Trigger):
	"""a trigger with the ability to move around and do cool stuff"""
	def __init__(self, *args, **kwargs):
		"""brain should be function in addition to trigger function to get called each turn"""
		Trigger.__init__(self, *args, **kwargs)
		self.brain = kwargs["brain_function"]
		self.x_vel, self.y_vel = 0, 0
		self.direction = 1

	def advance(self, game):
		Trigger.advance(self, game)
		self.brain(self, game) #hit detection will have to go in here
		self.x += self.x_vel
		self.y += self.y_vel

	def draw(self, destination):
		GamePiece.draw(self, destination)

if __name__ == "__main__":
	# TEST ROOM :)
	SCOREKEEP = pygame.font.SysFont("helvetica", 40)
	beerpile = [(100, 440), (300, 440), (500, 440), (300, 280)]
	def advance_frame(gameboard, CLOCK, SCREEN):
		CLOCK.tick(30)
		if DEBUG: os.system("clear||cls")
		if not gameboard["collectables"]: 
			gameboard["collectables"] = [GamePiece(x, y, 20, 20, name="beer", tangible=False, color=(210, 180, 200)) for (x, y) in beerpile]
		for peice in gameboard["platforms"] + [gameboard["player"]] + gameboard["triggers"] + gameboard["collectables"]:
			peice.advance(gameboard)
			peice.draw(SCREEN)
		SCREEN.blit(SCOREKEEP.render("Beers drank: "+str(len(gameboard["player"].collectables)), 0, (0, 0, 0)), (50, 50))


	SCREEN = pygame.display.set_mode((640, 480))
	PLAYER = {
		"name": "player",
		"color": (100, 50, 100),
		"grav": 1,
		"jump_vel": -15,
		"jumps": 2,
		"dash": True,
		"dash_speed": 14,
		"dash_frames": 25,
		"walk_speed": 8,
		"speed": 1,
		"friction": 1,
	}

	def walker(self, game):
		self.direction = -1 if self.x > game["player"].x else 1
		self.x_vel = self.speed * self.direction
	def kill(self, game):
		game["player"] = Player(50, 50, 30, 40, **PLAYER)
		self.triggered = False
	COP = {
		"name": "granny",
		"color": (250, 55, 55),
		"direction": 1,
		"speed": 3,
		"trigger_function": kill,
		"brain_function": walker
	}	


	wall = GamePiece(200, 320, 20, 140, name="door", tangible=True, color=(180, 150, 120))
	def door(self, game):
		order = [(200, 320),(200, 180),(420, 180),(420, 320)]
		self.x, self.y = wall.x, wall.y
		self.wall.x, self.wall.y = order[(order.index((wall.x, wall.y)) + 1) % 4]
		self.triggered = False

	TRIGGER = {
		"trigger_function": door,
		"name": "doortrigger",
		"color": (20, 150, 50),
		"wall": wall
	}
	gameboard = {
		"player": Player(50, 50, 30, 40, **PLAYER),
		"platforms": [wall] + [GamePiece(x, y, w, h, name="platform", color=(150, 150, 100))
		for x, y, w, h in [(0, 460, 640, 20), (620, 0, 20, 460), (0, 0, 20, 460), (200, 300, 240, 20)]],
		"triggers": [Trigger(420, 320, 20, 140, **TRIGGER), Enemy(600, 420, 30, 40, **COP)],
		"collectables": [GamePiece(x, y, 20, 20, name="beer", color=(210, 180, 200)) for (x, y) in beerpile]
	}
	while True:
		SCREEN.fill((255, 255, 255))
		advance_frame(gameboard, CLOCK, SCREEN)
		pygame.display.update()
