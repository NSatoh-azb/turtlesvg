# -*- coding: utf-8 -*-
"""
シェルピンスキーのガスケット（作成途中版）
"""

import turtlesvg as ttl
t = ttl.MyTurtle()
t.speed(10)
# t.tracer(0)

def middle_pt(A, B):
    # ABの中点を返す
    return ( (A[0] + B[0]) / 2, (A[1] + B[1]) / 2 )

def draw_triangle(A, B, C):
    t.penup()
    t.goto(A)
    t.pendown()

    t.goto(B)
    t.goto(C)
    t.goto(A)


def sierpinski(A, B, C, n=5):
    if n > 0:
        P = middle_pt(A, B)
        Q = middle_pt(B, C)
        R = middle_pt(C, A)

        draw_triangle(P, Q, R)
        
        sierpinski(A, P, R, n-1) 
        sierpinski(B, Q, P, n-1) 
        sierpinski(C, R, Q, n-1) 

#A = ( * , * )
B = (-300, -300)
#C = ( * , * ) # Hint: √3は、「3**0.5」で計算できる

#sierpinskiを実行 # ここまで出来たら1度実行してみよ

# 上の結果を見てあと1行、何かを追加したくなるはず・・・

t.penup()
t.save_as_svg('toi34_sierpinski.svg')
