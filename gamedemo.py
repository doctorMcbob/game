#rewrite
from __future__ import print_function, unicode_literals
import pygame
from pygame.locals import *
import os, sys
DEBUG = True if 'debug' in sys.argv else False

import gamepieces as gp

pygame.init()

SCREEN = pygame.display.set_mode((1280, 700))
CLOCK = pygame.time.Clock()

def makeplatform(rect):
	return {
		"name": "platform",
		"color": (150, 150, 100),
		"rect": pygame.rect.Rect(rect)
	}

def player_jump(this, game):
	if this['state'] == "stand":
		this['jumps'] = 2

PLAYER = {
	"name": "player",
	"color": (100, 50, 100),
	"grav": 1,
	"jump vel": -15,
	"jumps": 2,
	"walk speed": 8,
	"speed": 2,
	"friction": 1,
	"state": None,
	"advance_function": player_jump,

	"x vel": 0,
	"y vel": 0,
	"direction": 1,

	"rect": pygame.rect.Rect(350, 150, 30, 40),
	"buttons": {
		"left": K_LEFT,
		"right": K_RIGHT,
		"jump": K_z,
		"action": K_x
	}
}

WALL = makeplatform((500, 420, 20, 140))
def door_trigger_function(this, game):
	rect, wall = this['rect'], this['wall']['rect']
	rect.x, rect.y = wall.x, wall.y
	wall.x, wall.y = this['order'][(this['order'].index((wall.x, wall.y)) + 1) % 4]

DOOR_TRIGGER = {
	"name": 'door trigger',
	"trigger function": door_trigger_function,
	"rect": pygame.rect.Rect(720, 420, 20, 140),
	"color": (20, 150, 50),
	"wall": WALL,
	"invisable": False if DEBUG else True,
	"order": [(500, 420),(500, 280),(720, 280),(720, 420)],
}
PLATFORMS = [makeplatform((1110, 560, 150, 20)), makeplatform((940, 400, 150, 20)), makeplatform((1110, 240, 150, 20))]
def platform_trigger_function(this, game):
	rect = this['rect']
	i = this['order'].index((rect.x, rect.y))
	game['platforms'].append(this['platforms'][(i + 1) % 3])
	rect.x, rect.y = this['order'][(i + 1) % 3]
	if this['platforms'][(i - 1) % 3] in game['platforms']:
		game['platforms'].remove(this['platforms'][(i - 1) % 3])
	 

PLATFORM_TRIGGER = {
	"name": 'platform trigger',
	"trigger function": platform_trigger_function,
	"rect": pygame.rect.Rect(1110, 460, 20, 100),
	"platforms": PLATFORMS,
	"color": (20, 150, 50),
	"invisable": False if DEBUG else True,
	"order": [(1110, 460), (1070, 300), (1110, 140)],
}

GAMEBOARD = {
	'player': PLAYER,
	'platforms': [PLATFORMS[0]] + [WALL] + [makeplatform(rect) for rect in [
	(300, 560, 640, 20), (920, 100, 20, 460), (300, 100, 20, 460), (500, 400, 240, 20),
	(0, 0, 20, 680), (0, 680, 1280, 20), (1260, 0, 20, 680), (0, 0, 1280, 20),
	]],
	'triggers': [DOOR_TRIGGER, PLATFORM_TRIGGER]
}

def advance_frame(GAMEBOARD, SCREEN):
	keys = gp.render_input(GAMEBOARD)
	CLOCK.tick(30)
	if DEBUG:
		os.system("clear||cls")
		print(GAMEBOARD["player"])
	for actor in GAMEBOARD["triggers"] + GAMEBOARD["platforms"] + [GAMEBOARD["player"]]:
		gp.move_and_collision(actor, GAMEBOARD["platforms"])
		gp.trigger(actor, GAMEBOARD["player"], GAMEBOARD)
		if "advance_function" in actor: actor["advance_function"](actor, GAMEBOARD)
		if not ('invisable' in actor and actor['invisable']): gp.draw(actor, SCREEN)

while True:
	SCREEN.fill((255, 255, 255))
	advance_frame(GAMEBOARD, SCREEN)
	pygame.display.update()