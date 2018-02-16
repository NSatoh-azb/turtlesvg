# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 05:14:42 2018

@author: NSatoh

シェルピンスキーガスケット　一筆書き版 k角形対応版
"""

import turtlesvg as ttl
t = ttl.MyTurtle()

t.speed(10)
t.tracer(0)

def var_sierpinski_k(length, k, n, r=0.5):
    if n > 0:
        for i in range(k):
            t.fd(length)
            t.left(360/k)
            var_sierpinski_k(length * r, k, n-1, r)

t.bgcolor('black')
t.pencolor('white')
var_sierpinski_k(100, 7, 4, r=0.5)
t.penup()
t.save_as_svg('sierpinski_hitofude2.svg', unit_width=0.5)

