#this should really be renamed tools or assets
from __future__ import print_function, unicode_literals
import pygame
from pygame.locals import *

pygame.init()

FONT = pygame.font.SysFont("helvetica", 10)
def draw(this, destination):
	pygame.draw.rect(destination, this['color'], this['rect'])
	destination.blit(FONT.render(this['name'], 0, (0,0,0)), (this['rect'].x, this['rect'].y))
	if 'state' in this:
		destination.blit(FONT.render(this['state'], 0, (0,0,0)), (this['rect'].x, this['rect'].y + 10))

def bar(player, SCREEN, MAX=1000):
	pygame.draw.rect(SCREEN, (0, 0, 0), pygame.rect.Rect(0, 0, 1280, 30))
	pygame.draw.rect(SCREEN, (255, 255, 255), pygame.rect.Rect(5, 5, 1270, 20))
	progress = sum([col['value'] for col in player['collectables']])
	pygame.draw.rect(SCREEN, (255, 0, 0), pygame.rect.Rect(5, 5, int((progress / float(MAX)) * 1270), 20))
	return True if progress / float(MAX) >= 1 else False

def render_input(game):
	if pygame.event.get(QUIT): quit()
	if "player" in game:
		player = game['player']

		for event in pygame.event.get():
			if event.type == KEYDOWN:
				
				if 'jumps' in player and player['jumps'] and event.key == player['buttons']['jump']:
					player['jumps'] -= 1
					player['y vel'] = player['jump vel']

				elif "action" in player and event.key == player['buttons']['action']:
					player['action']()

		keys = pygame.key.get_pressed()	
		if keys[player['buttons']['left']] != keys[player['buttons']['right']]:
			player['direction'] = -1 if keys[player['buttons']['left']] else 1
			player['x vel'] = player['x vel'] + (player["speed"] * player['direction'])
			if not (0-player['walk speed'] < player['x vel'] < player['walk speed']):
				player['x vel'] = player['walk speed'] * player['direction']
	return keys

def  move_and_collision(this, checklist, screen):
	if not ('rect' in this and 'x vel' in this and 'y vel' in this and 'direction' in this):
		return
	checklist = [actor['rect'] for actor in checklist]
	rect = this['rect']

	# check for platform inside
	i = rect.collidelist(checklist)
	if i != -1:
		r1, r2 = rect, checklist[i]
		warp = {
			abs(r1.top - r2.bottom): (r1.x, r2.bottom), 
			abs(r1.bottom - r2.top): (r1.x, r2.top - r1.h), 
			abs(r1.left - r2.right): (r2.right, r1.y) ,
			abs(r1.right - r2.left): (r2.left - r1.w, r1.y),
		}
		rect.x, rect.y = warp[min(warp)]

 	# -- Y -- 
	if 'grav' in this: this['y vel'] += this['grav']
	yi = rect.move(0, this['y vel']).collidelist(checklist)
	if yi != -1:		
		if this['y vel'] > 0:
			if 'state' in this: this['state'] = "stand"
			# velocity correction
			while checklist[yi].colliderect(pygame.rect.Rect(
						rect.left, rect.bottom, rect.w, this['y vel']
					)):
					this['y vel'] -= 1
		else: 
			while checklist[yi].colliderect(pygame.rect.Rect(
						rect.left, rect.top + this['y vel'], rect.w, this['y vel']
					)): 
				this['y vel'] += 1

		if "friction" in this and this['x vel']:
			this['x vel'] = this['x vel'] - this['friction'] if this['x vel'] > 0 else this['x vel'] + this['friction']
	if 'state' in this and this['y vel']: this['state'] = 'fall'
	
	# -- X -- 
	xi = rect.move(this['x vel'], 0).collidelist(checklist)
	if xi != -1:
		# velocity correction
		while checklist[xi].colliderect(pygame.rect.Rect(
			*[
					((rect.left + this["x vel"], rect.top), (abs(this['x vel']), rect.h)), "sneaky",
					((rect.right, rect.top), (abs(this["x vel"]), rect.h)) 
				][this['direction'] + 1])  ):
			this['x vel'] -= this["direction"]

	rect.move_ip(this['x vel'], this['y vel'])

	# check for platform inside again
	i = rect.collidelist(checklist)
	if i != -1:
		r1, r2 = rect, checklist[i]
		warp = {
			abs(r1.top - r2.bottom): (r1.x, r2.bottom), 
			abs(r1.bottom - r2.top): (r1.x, r2.top - r1.h), 
			abs(r1.left - r2.right): (r2.right, r1.y) ,
			abs(r1.right - r2.left): (r2.left - r1.w, r1.y),
		}
		rect.x, rect.y = warp[min(warp)]


def trigger(this, check, game):
	if not ('rect' in this and 'trigger function' in this):
		return
	if this['rect'].colliderect(check['rect']): this['trigger function'](this, game)
