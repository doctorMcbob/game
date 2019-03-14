# GamePiece class documentation

the engine as it stands calls advance on all game peices once per frame. i will problably build a better handler when i finish with the peices. 

## GamePiece:
	good for platforms and collectables
	. inherets from Pygame.Rect
	. includes draw to destination
	. advance function 
		. just passes, other classes overwrite with more interesting things

## Player:
	The bulk of the code right now
	. inherets GamePiece
	. overwrites advance 
		. hit dection 
		. dash functionality 
		. handles input with helper function
	. includes render_input
		. exausts pygame event que
		. resolves relevent events

##Trigger:
	Requires you to pass a function which triggers on collision
	. inherets Gamepiece
	. advance overwritten
		. hit detection for Player
		. turns off on collision
		. runs trigger function
			. trigger function is expected to turn trigger back on
	. invisible unless DEBUG mode is on

##Enemy:
	Trigger on Wheels. Requires 2 functions, one called every loop, and one called on collision
	. inherets Trigger
	. overwrites advance
		. includes trigger advance function
		. runs brain function
		. moves by x y velocity