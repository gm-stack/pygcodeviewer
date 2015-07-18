#!/usr/bin/env python

import sys
import pygame

#######
extrude_colour = (255,255,255)
move_colour = (0,255,0)
screen_res = (320,240)
#######

pygame.init()
screen = pygame.display.set_mode(screen_res)
screen.fill((0,0,0))

layers = []
layernum = 0

gcode_lines = open(sys.argv[1]).readlines()

#
position = [0,0,0]
#

def scale(x,y):
	x -= xmin
	y -= ymin
	x *= sf
	y *= sf
	return (x+xoff,y+yoff)

def parse_gcode_args(gcode):
	gcode = gcode.split(";")[0].split()
	if not gcode: return (None, None)
	command = gcode[0]
	params = {item[0]: item[1:] for item in gcode[1:]}
	return (command, params)

def gcode_layerchange(params):
	position[2] = float(params['Z'])
	screen.fill((0,0,0))
	pygame.display.update()

def G1_move(params):
	oldposition = list(position)
	if 'X' in params: position[0] = float(params['X'])
	if 'Y' in params: position[1] = float(params['Y'])
	print params
	oldpos_s = map(int,scale(*oldposition[0:2]))
	pos_s = map(int, scale(*position[0:2]))
	lines = (oldpos_s, pos_s)
	line_colour = extrude_colour if 'E' in params else move_colour
	pygame.draw.lines(screen, line_colour, False, lines, 1)
	#pygame.display.update()

def get_bounds():
	global xmin, xmax, ymin, ymax, sf, xoff, yoff

	xmin, xmax = sys.maxint, 0
	ymin, ymax = sys.maxint, 0

	for gcode_line in gcode_lines:
		command, params = parse_gcode_args(gcode_line.strip())
		if command == "G1":
			if "X" in params and "Y" in params:
				X, Y = float(params["X"]), float(params["Y"])
				if X < xmin: xmin = X
				if X > xmax: xmax = X
				if Y < ymin: ymin = Y
				if Y > ymax: ymax = Y

	xw = xmax - xmin
	yw = ymax - ymin

	sf = 0
	xoff, yoff = 0, 0
	if xw > yw:
		sf = float(screen_res[1]-1) / yw
		print "scaling down because Y"
		xoff = int((screen_res[0] - (xw * sf))/2.0)
	else:
		sf = float(screen_res[0]-1) / xw
		print "scaling down because X"
		yoff = int((screen_res[1] - (yw * sf))/2.0)

gcode_lineno = 0
def gcode_nextline():
	global gcode_lineno
	gcode_line = gcode_lines[gcode_lineno].strip()
	command, params = parse_gcode_args(gcode_line)
	if command == "G1":
		if "Z" in params:
			gcode_layerchange(params)
		else:
			G1_move(params)
	gcode_lineno += 1


pygame.display.update()

get_bounds()

while True:
	event = pygame.event.wait()
	if event.type == pygame.QUIT:
		print "quitting"
		pygame.quit()
		sys.exit()
	elif event.type == pygame.KEYDOWN:
	    if event.key == pygame.K_RIGHT:
	    	#for i in range(100):
	        gcode_nextline()
	        pygame.display.update()