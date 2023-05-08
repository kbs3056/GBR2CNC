import os
import sys
import re
from turtle import Screen, Turtle
import numpy as np

safe_Z_h = "5.000"
start_Z_h = "2.000"
end_Z_h = "0.000"
travel_feedrate = "600"
Z_travel_feedrate = "300"
XY_feedrate = "275"
Z_feedrate = "50"
Dwell = "3"

preamble = """(KBS3056 GBR2CNC PCB Cutout script)
G17 G54 G40 G49 G80 G90
G64 P0.007
G21
G54  

"""
postamble = """
G17 G54 G90 G80 G40
M2
"""

#kicad  D10*;  X29100000Y-174500000D02*  mm
#gerbv  G54D10*;  G01X1145669Y-6870079D02*  in

kicad = -1
gerbv = -1
inch = -1
f_line_n = -1
x = 0
y = 0
x_min, x_max, y_min, y_max = (None,) * 4
g_line_start_x = []
g_line_start_y = []
g_line_end_x = []
g_line_end_y = []
turt_line = []

f = open(sys.argv[1], "r")
f_lines = f.readlines()
f.close()

file_name = os.path.abspath(sys.argv[1])
#file_name = os.path.basename(sys.argv[1])
file_name = os.path.splitext(file_name)[0]
f = open(file_name + ".ngc", "w")

f.write(preamble)
for f_line in f_lines:
	f_line_n = f_line_n + 1
	
	if re.search(r"\A%MOIN\*%", f_line):
		inch = f_line_n
	if re.search(r"\AD10\*", f_line): ###
		kicad = f_line_n
	if re.search(r"\AG54D10\*", f_line):
		gerbv = f_line_n
	
	if kicad != -1 or gerbv != -1:
		if re.search(r"\S+" "D02\*", f_line):
			x = re.search(r"X(\-?\d+)", f_line).group(1)
			if inch != -1:
				x = str(int(x[:-1])*254)
			g_line_start_x.append(x)
			x = re.search(r"Y(\-?\d+)", f_line).group(1)
			if inch != -1:
				x = str(int(x[:-1])*254)
			g_line_start_y.append(x)
		if re.search(r"\S+" "D01\*", f_line):
			x = re.search(r"X(\-?\d+)", f_line).group(1)
			if inch != -1:
				x = str(int(x[:-1])*254)
			g_line_end_x.append(x)
			x = re.search(r"Y(\-?\d+)", f_line).group(1)
			if inch != -1:
				x = str(int(x[:-1])*254)
			g_line_end_y.append(x)
			
print("\nLines count: " + str(len(g_line_start_y)))
print("\nThis version only supports lines in the third quadrant! Others will be misinterpreted!")
print("\nMake sure the G-code was generated correctly, by checking it in the simulator or by doing \"air cutting\"!\n")

#sorting, line start higher than end. supports only III (and I, after changing direction) quadrant!
for arr_line in range (len(g_line_start_y)):
	if int(g_line_start_x[arr_line]) < int(g_line_end_x[arr_line]):
		g_line_start_x[arr_line], g_line_end_x[arr_line] = g_line_end_x[arr_line], g_line_start_x[arr_line]
	if int(g_line_start_y[arr_line]) < int(g_line_end_y[arr_line]):
		g_line_start_y[arr_line], g_line_end_y[arr_line] = g_line_end_y[arr_line], g_line_start_y[arr_line]
#

#calculating screen coordinates
x_max = int(g_line_start_x[0][:-6])
y_max = int(g_line_start_y[0][:-6])
x_min = int(g_line_end_x[0][:-6])
y_min = int(g_line_end_y[0][:-6])
for arr_line in range (len(g_line_start_y)):
	if x_min > int(g_line_end_x[arr_line][:-6]):
		x_min = int(g_line_end_x[arr_line][:-6])
	if y_min > int(g_line_end_y[arr_line][:-6]):
		y_min = int(g_line_end_y[arr_line][:-6])
	if x_max < int(g_line_start_x[arr_line][:-6]):
		x_max = int(g_line_start_x[arr_line][:-6])
	if y_max < int(g_line_start_y[arr_line][:-6]):
		y_max = int(g_line_start_y[arr_line][:-6])
#

screen = Screen()
screen.title("KBS3056 GBR2CNC PCB Cutout script")
screen.delay(20) # animation speed
screen.setworldcoordinates(x_min - 30, y_min - 2, x_max + 30, y_max + 2)
screen.bgcolor("#B0C0C0")
for arr_line in range (len(g_line_start_y)):
	turt_line.append(Turtle())
	turt_line[arr_line].hideturtle()
	turt_line[arr_line].shape("circle")
	turt_line[arr_line].shapesize(0.4)
	turt_line[arr_line].pensize(2.5)
	turt_line[arr_line].fillcolor("red")
	turt_line[arr_line].showturtle()
	turt_line[arr_line].penup()
	turt_line[arr_line].goto(int(g_line_start_x[arr_line][:-6]), int(g_line_start_y[arr_line][:-6]))
	#turt_line[arr_line].write(arr_line, align="right", font=("Arial", 12))
	turt_line[arr_line].pendown()
	x = np.array([int(g_line_start_x[arr_line][:-6]), int(g_line_end_x[arr_line][:-6])])
	y = np.array([int(g_line_start_y[arr_line][:-6]), int(g_line_end_y[arr_line][:-6])])
	turt_line[arr_line].goto(int(np.mean(x)), int(np.mean(y)))
	turt_line[arr_line].write(str(arr_line) + " ", align="right", font=("Arial", 12, "bold"))
	turt_line[arr_line].goto(int(g_line_end_x[arr_line][:-6]), int(g_line_end_y[arr_line][:-6]))
	#turt_line[arr_line].write(arr_line, align="right", font=("Arial", 12))
	
print("Now type lines numbers in the desired order.")	
order = input(">>> Milling order: ")
#screen.mainloop()
order = re.split(r"\W+", order)
print("\nOrder: " + str(order))
assert len(order) == len(g_line_start_y), "Type numbers of all displayed lines, separeted like: \"0,1,2,3\" or \"0 1 2 3\" or \"0;1;2;3\" or \"0, 1, 2, 3\"!"
for number in range (len(order)):
	assert re.search(r"(\d)", order[number]), "Type numbers only!"
	assert int(order[number]) < len(g_line_start_y), "Type numbers in range [0:" + str(len(g_line_start_y) - 1) + "]!"
assert len(order) == len(set(order)), "All numbers must be unique!"

#gcode generator
f.write("G4 P" + Dwell + "\n\n")
for arr_line in range (len(g_line_start_y)):
	x = re.search(r"(\-?\d+)(\d{6}$)", g_line_start_x[int(order[arr_line])])
	x = x.group(1) + "." + x.group(2)[:3]
	y = re.search(r"(\-?\d+)(\d{6}$)", g_line_start_y[int(order[arr_line])])
	y = y.group(1) + "." + y.group(2)[:3]
	f.write("G0 Z" + safe_Z_h + " F" + Z_travel_feedrate + "\n")
	f.write("G0 X" + x + " Y" + y + " F" + travel_feedrate + "\n")
	f.write("G0 Z" + start_Z_h + " F" + Z_travel_feedrate + "\n")
	f.write("G1 Z" + end_Z_h + " F" + Z_feedrate + "\n")
	x = re.search(r"(\-?\d+)(\d{6}$)", g_line_end_x[int(order[arr_line])])
	x = x.group(1) + "." + x.group(2)[:3]
	y = re.search(r"(\-?\d+)(\d{6}$)", g_line_end_y[int(order[arr_line])])
	y = y.group(1) + "." + y.group(2)[:3]
	f.write("G1 X" + x + " Y" + y + " F" + XY_feedrate + "\n\n")
f.write("G0 Z" + safe_Z_h + " F" + Z_travel_feedrate + "\n")
f.write("G0 X" + str(x_max) + " Y" + str(y_max) + " F" + Z_travel_feedrate + "\n") # collision caution! move out to the top right corner of the bounding box!
#

f.write(postamble)
f.close()
f_lines[:] = []		
