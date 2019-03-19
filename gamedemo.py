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

	"rect": pygame.rect.Rect(50, 50, 30, 40),
	"buttons": {
		"left": K_LEFT,
		"right": K_RIGHT,
		"jump": K_z,
		"action": K_x
	}
}

GAMEBOARD = {
	'player': PLAYER,
	'platforms': [makeplatform(rect) for rect in [
	(0, 460, 640, 20), (620, 0, 20, 460), (0, 0, 20, 460), (200, 300, 240, 20)]],
	'triggers': []
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
		gp.draw(actor, SCREEN)
	

while True:
	SCREEN.fill((255, 255, 255))
	advance_frame(GAMEBOARD, SCREEN)
	pygame.display.update()