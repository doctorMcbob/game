#gamedemo.py
from __future__ import unicode_literals, print_function
import pygame
from pygame.locals import *
from gamepieces import *
import sys
DEBUG = 'debug' in sys.argv

pygame.init()

SCREEN = pygame.display.set_mode((640, 480))
SCREEN.fill((255, 255, 255))
pygame.display.update()
CLOCK = pygame.time.Clock()
SCOREKEEP = pygame.font.SysFont("helvetica", 40)

# PLAYER FUNCTIONS
def dash(self, game):
	self.x_vel = 40 # make better later

# TRIGGER FUNCTIONS
def kill(self, game):
	game["player"] = Player(50, 50, 30, 40, **PLAYER)
	self.triggered = False

def door_trigger(self, game):
	order = [(200, 320),(200, 180),(420, 180),(420, 320)]
	self.x, self.y = self.wall.x, self.wall.y
	self.wall.x, self.wall.y = order[(order.index((self.wall.x, self.wall.y)) + 1) % 4]
	self.triggered = False

# ENEMY FUNCTIONS
def walker(self, game):
	self.direction = -1 if self.x > game["player"].x else 1
	self.x_vel = self.speed * self.direction

# GAME ACTORS
PLAYER = {
	"name": "player",
	"color": (100, 50, 100),
	"grav": 1,
	"jump_vel": -15,
	"jumps": 2,
	"action_function": dash,
	"walk_speed": 8,
	"speed": 1,
	"friction": 1,
}

COP = {
	"name": "granny",
	"color": (250, 55, 55),
	"direction": 1,
	"speed": 3,
	"trigger_function": kill,
	"brain_function": walker
}	

TRIGGER = {
	"trigger_function": door_trigger,
	"name": "doortrigger",
	"color": (20, 150, 50),
	"wall": GamePiece(200, 320, 20, 140, name="door", tangible=True, color=(180, 150, 120))
}

# ASSEMLE GAME BOARD
beerpile = [(100, 440), (300, 440), (500, 440), (300, 280)]
gameboard = {
	"player": Player(50, 50, 30, 40, **PLAYER),
	"platforms": [TRIGGER["wall"]] + [GamePiece(x, y, w, h, name="platform", color=(150, 150, 100))
	for x, y, w, h in [(0, 460, 640, 20), (620, 0, 20, 460), (0, 0, 20, 460), (200, 300, 240, 20)]],
	"triggers": [Trigger(420, 320, 20, 140, **TRIGGER), Enemy(600, 420, 30, 40, **COP)],
	"collectables": [GamePiece(x, y, 20, 20, name="beer", color=(210, 180, 200)) for (x, y) in beerpile]
}

def advance_frame(gameboard, CLOCK, SCREEN):
	CLOCK.tick(30)
	if DEBUG: os.system("clear||cls")
	if not gameboard["collectables"]: 
		gameboard["collectables"] = [GamePiece(x, y, 20, 20, name="beer", tangible=False, color=(210, 180, 200)) for (x, y) in beerpile]
	for peice in gameboard["platforms"] + [gameboard["player"]] + gameboard["triggers"] + gameboard["collectables"]:
		peice.advance(gameboard)
		peice.draw(SCREEN)
	SCREEN.blit(SCOREKEEP.render("Beers drank: "+str(len(gameboard["player"].collectables)), 0, (0, 0, 0)), (50, 50))


while True:
	SCREEN.fill((255, 255, 255))
	advance_frame(gameboard, CLOCK, SCREEN)
	pygame.display.update()
