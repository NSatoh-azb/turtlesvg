# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 06:41:56 2018

問37 コッホ曲線

"""

import turtlesvg as ttl
t = ttl.MyTurtle()

def koch(n, l):
    if n == 0:
        t.fd(l)
    else:
        koch(n-1, l/3)
        # 向きを変える
        koch(n-1, l/3)
        # 向きを変える
        koch(n-1, l/3)
        # 向きを変える
        koch(n-1, l/3)

t.penup()
t.goto(-300,-200)
t.pendown()

t.speed(0)
#t.tracer(0)

koch(4, 600)
t.update()

t.penup()
t.save_as_svg('toi37_koch.svg')

