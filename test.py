# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:41:04 2018

@author: NSatoh
"""

import turtlesvg as ttl
import math

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

def koch_test(t):
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
 
def dot_test(t):
    t.penup()
    t.speed(10)
    t.tracer(0)
    
    t.goto(200, 200)

    for i in range(360):
        c = math.cos(math.radians(i))
        s = math.sin(math.radians(i))
        r = (i**2)/100
        size = i/10
        t.goto(r*c, r*s)
        t.dot(size, i/360, 0.5, i/720)

    t.update()    
    t.save_as_svg('dot_test.svg')
    


if __name__ == '__main__':
    t1 = ttl.Turtle()
    koch_test(t1)
    t2 = ttl.Turtle()
    dot_test(t2)
    