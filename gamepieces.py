from __future__ import unicode_literals, print_function
import pygame
from pygame.locals import *
import sys, os
DEBUG = 'debug' in sys.argv

pygame.init()
FONT = pygame.font.SysFont("helvetica", 10)
CLOCK = pygame.time.Clock()

class GamePiece(object):
	"Anything with the daunting task of appearing on screen"
	def __init__(self, *args, **kwargs):
		"""let args be rect arguments"""
		self.name = kwargs["name"]
		self.rect = pygame.Rect(*args)
		self.x, self.y = self.rect.x, self.rect.y
		self.w, self.h = self.rect.w, self.rect.h
		self.color = kwargs["color"]

	def draw(self, destination):
		pygame.draw.rect(destination, self.color, self.rect)
		destination.blit(FONT.render(self.name, 0, (0, 0, 0)),
		(self.rect.x, self.rect.y))

	def advance(self, game):
		pass


class Player(GamePiece):
	def __init__(self, *args, **kwargs):
		GamePiece.__init__(self, *args, **kwargs)
		self.x_vel = 0
		self.y_vel = 0
		self.direction = 1 #pos = right, neg = left

		self.grav = 2
		self.jump_vel = -30
		self.jumps = 2
		self.dash = True
		self.dash_speed = 20
		self.dash_frames = 5
		self.dash_counter = 0
		self.walk_speed = 8
		self.speed = 1
		self.friction = 3

		self.keys = pygame.key.get_pressed()
		self.buttons = {
			"left": K_LEFT,
			"right": K_RIGHT,
			"jump": K_z,
			"dash": K_x
		}

	def _debug_display(self):
		if not DEBUG: return
		os.system('clear||cls')
		print(self.name)
		print("x, y:", self.x, self.y)
		print("x_vel, y_vel: ", self.x_vel, self.y_vel)
		print("direction: ", self.direction)
		print("jumps: ", self.jumps)
		print("dash counter, dash frames: ", self.dash_counter, self.dash_frames)
		print("Buttons:")
		for btn in self.buttons:
			print("   ", btn, ":", self.keys[self.buttons[btn]])

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
				if event.key == self.buttons['left']:
					self.direction = -1
				if event.key == self.buttons['right']:
					self.direction = 1

		self.keys = pygame.key.get_pressed()
		self.x_vel = max(
			min(abs(self.x_vel) + (self.speed * (self.keys[self.buttons['right']] or self.keys[self.buttons['left']])), self.walk_speed),
			abs(self.x_vel)
		) * self.direction


	def advance(self, game):
		self._debug_display()
		self.render_input()
		platforms = filter(lambda x: x.name=="platform", game)
		# Y update and hit detection
		self.y_vel += self.grav	

		if self.rect.move(0, self.y_vel).collidelist(
			[x.rect for x in platforms]) != -1:
			#landing
			if self.y_vel > 0: 
				self.jumps = 2
			self.y_vel = 0

			if abs(self.x_vel) and self.dash:
				if (self.keys[self.buttons['right']] or self.keys[self.buttons['left']]):
					self.x_vel = max(abs(self.x_vel) - self.friction, self.walk_speed
						) * self.direction
				else:
					self.x_vel = max(abs(self.x_vel) - self.friction, 0
						) * self.direction

		# X update and hit detection
		if not self.dash:
			self.dash_counter += 1
			if self.dash_counter == self.dash_frames:
				self.dash = True
				self.dash_counter = 0
		if self.rect.move(self.x_vel, 0).collidelist(
			[x.rect for x in platforms]) != -1:
			self.x_vel = 0

		#cornerbug fix
		if self.rect.move(self.x_vel, self.y_vel).collidelist(
			[x.rect for x in platforms]) != -1:
			self.x_vel, self.y_vel = 0, 0

		self.x += self.x_vel
		self.y += self.y_vel
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		

def advance_frame(gameboard, CLOCK, SCREEN):
	CLOCK.tick(30)
	for peice in gameboard:
		peice.advance(gameboard)
		peice.draw(SCREEN)


if __name__ == "__main__":
	# TEST ROOM :)

	SCREEN = pygame.display.set_mode((640, 480))

	gameboard = []
	gameboard.append(GamePiece(0, 460, 640, 20, 
		name="platform", color=(150, 150, 100)))
	gameboard.append(GamePiece(620, 0, 20, 460, 
		name="platform", color=(150, 150, 100)))
	gameboard.append(GamePiece(0, 0, 20, 460, 
		name="platform", color=(150, 150, 100)))
	gameboard.append(GamePiece(200, 300, 100, 20, 
		name="platform", color=(150, 150, 100)))

	player = Player(50, 50, 30, 40, 
		name="player", color=(100, 50, 100))
	gameboard.append(player)

	while True:
		SCREEN.fill((255, 255, 255))
		advance_frame(gameboard, CLOCK, SCREEN)
		pygame.display.update()
