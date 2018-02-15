# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:41:04 2018

@author: NSatoh
"""

import turtlesvg as ttl

def koch_r(t, length, n):
    if n == 0:
        t.fd(length)
    else:
        koch_r(t, length/3, n-1)
        t.right(60)
        koch_r(t, length/3, n-1)
        t.left(120)
        koch_r(t, length/3, n-1)
        t.right(60)
        koch_r(t, length/3, n-1)
    
t = ttl.MyTurtle()
t.tracer(0)
t.speed(10)

t.pu()
t.goto(300, 0)
t.pd()

t.bgcolor('skyblue')
t.fillcolor('yellow')

t.begin_fill()
k = 1
t.right(72)
t.pencolor('red')
colors = ['blue', 'red', 'green', 'purple']
koch_r(t, 300, k)
for i in range(4):
    t.right(144)
    t.pencolor(colors[i])
    koch_r(t, 300, k)
t.fd(100)
for i in range(3):
    t.circle(50, 120)
    t.fd(50)
t.fd(100)
t.circle(150)
t.fd(150)
t.circle(100, 3600, 17)
t.end_fill()

t.pu()
t.update()
t.save_as_svg('turtlesvg_test_output.svg', unit_length=1, unit_width=2)
