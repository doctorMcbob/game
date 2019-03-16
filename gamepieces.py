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

