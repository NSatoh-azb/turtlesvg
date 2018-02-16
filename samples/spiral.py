# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 01:49:12 2018

@author: NSatoh

螺旋を描く．
"""

import turtlesvg as ttl

t = ttl.MyTurtle()

t.speed(10)
t.ht()
t.tracer(0)

def spiral(a, d=5, n=0, n_max=300):
    if n < n_max:
        t.fd(n)
        t.rt(a)
        spiral(a, d, n+d, n_max)
        t.update()        


# -- 以下は授業プリントと同じサンプル --------


#spiral(90)
#spiral(72)
spiral(71, d=1)

t.penup()
t.save_as_svg('spiral_sample.svg')