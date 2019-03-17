#rewrtite
import pygame
from pygame.locals import *

pygame.init()

FONT = pygame.font.SysFont("helvetica", 10)
def draw(this, destination):
	pygame.draw.rect(destination, this['color'], this['rect'])
	destination.blit(FONT.render(this['name'], 0, (0,0,0), (
	this['rect'].x, this['rect'].y)))

def render_input(game):
	if pygame.event.get(QUIT): quit()
	if "player" in game:
		player = game['player']

		for event in pygame.event.get():
			if event.type == KEYDOWN:
				
				if 'jumps' in player and player['jumps'] and
				event.key == player['buttons']['jump']:
					player['jumps'] -= 1
					player['y vel'] = player['jump vel']

				elif "action" in player and 
				event.key == player['buttons']['action']:
					player['action']()

		keys = pygame.keys.get_pressed()	
		if keys[player['buttons']['left']] != keys[player['buttons']['right']]:
			player['direction'] = -1 if keys[player['buttons']['left']] else 1
			player['x vel'] = max(
				min(abs(player['x vel']) + player["speed"], 
					player['walk speed']),
				abs(player['x vel'])
			) * player['direction']
	return keys

def  move_and_collision(this, checklist):
	if not ('rect' in this and 'x vel' in this and 'y vel' in this and 'direction' in this):
		return
	rect = this['rect']
	# -- Y -- 
	i = rect.move(0, this['y vel']).collidelist(checklist)
	if i != -1:
		if this['y vel'] > 0:
			if 'state' in this: this['state'] = "stand"
			# velocity correction
			while checklist[i].colliderect(pygame.rect.Rect(
						rect.left, rect.bottom, rect.w, this['y vel']
					)): this['y vel'] -= 1
		else: this['y vel'] = 0
		if "friction" in this and this['x vel']:
			this['x vel'] = (abs(this['x vel']) - this['friction']) * this['direction']
	else:
		if 'grav' in this:
			this['y vel'] -= this['grav']
	# -- X -- 
	i = rect.move(0, this['x vel']).collidelist(checklist)
	if i != -1:
		# velocity correction
		while checklist[i].colliderect(pygame.rect.Rect(
					*[
							((rect.left + this["x vel"], rect.top), (abs(this['x vel']), rect.h)), "sneaky",
							((rect.right, rect.top), (abs(this["x vel"]), rect.h)) 
						][self.direction + 1])  ):
					this['x vel'] -= this["direction"]

	#cornerbug fix
	if rect.move(this['x vel'], this['y vel']).collidelist(checklist) != -1:
		this['x vel'], this['y vel'] = 0, 0

	rect.move_ip(this['x vel'], this['y vel'])

def trigger(this, check, game):
	if not ('rect' in this and 'trigger_function' in this):
		return
	if this['rect'].colliderect(check): this['trigger_function'](game)

def player_base(name, (x, y)):
	return {
		"name": name,
		"x vel": 0,
		"y vel": 0,
		"direction": 1,
		"rect": pygame.rect.Rect(x, y, 30, 40)
		"color": (100, 50, 100), 
		"state": None
	}