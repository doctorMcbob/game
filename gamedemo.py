from __future__ import print_function, unicode_literals
import pygame
from pygame.locals import *
import os, sys
DEBUG = True if 'debug' in sys.argv else False

import gameassets as ga

pygame.init()

SCREEN = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Alcoholism: The Game")
CLOCK = pygame.time.Clock()


def door_trigger_function(this, game):
	rect, wall = this['rect'], this['wall']['rect']
	rect.x, rect.y = wall.x, wall.y
	wall.x, wall.y = this['order'][(this['order'].index((wall.x, wall.y)) + 1) % 4]
	

def platform_trigger_function(this, game):
	rect = this['rect']
	i = this['order'].index((rect.x, rect.y))
	game['platforms'].append(this['platforms'][(i + 1) % 3])
	rect.x, rect.y = this['order'][(i + 1) % 3]
	if this['platforms'][(i - 1) % 3] in game['platforms']:
		game['platforms'].remove(this['platforms'][(i - 1) % 3])
	 
def reset_platforms(this, game):
	for plat in this['platforms']:
		if plat in GAMEBOARD['platforms']:
			GAMEBOARD['platforms'].remove(plat)
	this['friend']['rect'] = pygame.rect.Rect(1110, 460, 20, 100)
	GAMEBOARD['platforms'].append(this['platforms'][0])

def granny_about(this, game):
	this['direction'] = 1 if this['rect'].x < game['player']['rect'].x else -1
	this['x vel'] = 1 * this['direction']

def turn_around(this, game):
	if this['x vel'] == 0:
		this['direction'] = [None, -1, 1][this['direction']]
	this['x vel'] = 8 * this['direction']

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
	"advance function": ga.player_jump,
	"collectables": [],

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

WALL = ga.makeplatform((500, 420, 20, 140))
DOOR_TRIGGER = {
	"name": 'door trigger',
	"trigger function": door_trigger_function,
	"rect": pygame.rect.Rect(720, 420, 20, 140),
	"color": (20, 150, 50),
	"wall": WALL,
	"invisable": False if DEBUG else True,
	"order": [(500, 420),(500, 280),(720, 280),(720, 420)],
}

PLATFORMS = [ga.makeplatform((1110, 560, 150, 20)), ga.makeplatform((940, 400, 150, 20)), ga.makeplatform((1110, 240, 150, 20))]
PLATFORM_TRIGGER = {
	"name": 'platform trigger',
	"trigger function": platform_trigger_function,
	"rect": pygame.rect.Rect(1110, 460, 20, 100),
	"platforms": PLATFORMS,
	"color": (20, 150, 50),
	"invisable": False if DEBUG else True,
	"order": [(1110, 460), (1070, 300), (1110, 140)],
}

RESET_TRIGGER = {
	"name": "platform reset trigger",
	"trigger function": reset_platforms,
	"rect": pygame.rect.Rect(920, 580, 20, 100),
	"color": (20, 150, 50),
	"invisable": False if DEBUG else True,
	"friend": PLATFORM_TRIGGER,
	"platforms": PLATFORMS,
}

GRANNY = {
	"name": "granny",
	"rect": pygame.rect.Rect(800, 500, 40, 60),
	"color": (250, 55, 55),
	"advance function": granny_about,
	"trigger function": ga.kill,
	"x vel": 1,
	"y vel": 0,
	"direction": -1
}

DOG = {
	"name": "dog",
	"rect": pygame.rect.Rect(20, 660, 40, 20),
	"color": (250, 55, 55),
	"advance function": turn_around,
	"trigger function": ga.kill,
	"x vel": 8,
	"y vel": 0, 
	"direction": 1,
}

beerpile = [(400, 540), (600, 540), (800, 540), (600, 380), (300, 80), (920, 80),
			(150, 150), (150, 250), (150, 350), (150, 450), (150, 550),
			(150, 660), (400, 660), (500, 660), (600, 660), (700, 660), (800, 660), 
			(1080, 660), (1080, 450), (1080, 350), (1080, 250), (1080, 150)]
GAMEBOARD = {
	'player': PLAYER,
	'platforms': [PLATFORMS[0]] + [WALL] + [ga.makeplatform(rect) for rect in [
	(300, 560, 640, 20), (920, 100, 20, 460), (300, 100, 20, 460), (500, 400, 240, 20),
	(0, 0, 20, 680), (0, 680, 1280, 20), (1260, 0, 20, 680), (0, 0, 1280, 20),
	]],
	'triggers': [DOOR_TRIGGER, PLATFORM_TRIGGER, RESET_TRIGGER, GRANNY, DOG],
	'collectables': [ga.makecollectable((xy, (20, 20)), "beer", 10) for xy in beerpile]
}

def advance_frame(GAMEBOARD, SCREEN):
	keys = ga.render_input(GAMEBOARD)
	CLOCK.tick(30)
	if DEBUG:
		os.system("clear||cls")
		print(GAMEBOARD["player"])
	for actor in GAMEBOARD["triggers"] + GAMEBOARD["platforms"] + [GAMEBOARD["player"] ]+ GAMEBOARD['collectables']:
		ga.move_and_collision(actor, GAMEBOARD["platforms"])
		ga.trigger(actor, GAMEBOARD["player"], GAMEBOARD)
		if "advance function" in actor: actor["advance function"](actor, GAMEBOARD)
	SCREEN.blit(ga.SCROLLER(SCREEN, GAMEBOARD["player"], GAMEBOARD["triggers"] + GAMEBOARD["platforms"] + GAMEBOARD['collectables']), (0, 0))
	if not GAMEBOARD['collectables']: GAMEBOARD['collectables'] = [ga.makecollectable((xy, (20, 20)), "beer", 10) for xy in beerpile]
	ga.bar(GAMEBOARD['player'], SCREEN)
	
while True:
	SCREEN.fill((255, 255, 255))
	advance_frame(GAMEBOARD, SCREEN)
	pygame.display.update()