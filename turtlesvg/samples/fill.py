# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 12:48:15 2020

@author: NSatoh
"""

import sys
sys.path.append('../')
import turtlesvg as ttl


t = ttl.Turtle()

t.fillcolor('red')

t.fd(100)
t.lt(60)

t.begin_fill()
t.fd(200)
t.lt(90)
t.pensize(5)
t.pencolor('blue')
t.fd(100)
t.lt(135)
t.fd(248)
t.end_fill()

t.fillcolor('yellow')
t.pensize(3)
t.pencolor('green')
t.begin_fill()
t.lt(120)
t.fd(100)
t.seth(180)
t.fd(150)
t.end_fill()


t.save_as_svg('fill_faithful_sample.svg')
t.set_faithful()
t.save_as_svg('fill_not_faithful_sample.svg')