# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 19:29:59 2018
@author: NSatoh

Koch island の色々なテスト

  ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
  ＊＊＊＊＊＊＊＊＊！！！　　重要　！！！＊＊＊＊＊＊＊＊＊
  ＊＊　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊　　Spyderで実行の前に必ず、右下のコンソール画面で　　　＊＊
  ＊＊　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊    In [1]: %gui tk　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊ 　を実行しておくこと！！　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　＊＊
  ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
  ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

"""

import turtlesvg as ttl
import math

def koch_angle(t, n, length, theta):
    if n == 0:
        t.fd(length)
    else:
        l1 = length/3
        l2 = l1 / (2*math.cos(math.radians(theta)))
        
        koch_angle(t, n-1, l1, theta)
        t.left(theta)
        koch_angle(t, n-1, l2, theta)
        t.right(2*theta)
        koch_angle(t, n-1, l2, theta)
        t.left(theta)
        koch_angle(t, n-1, l1, theta)


def test0(n=4, length=200, theta=60):
    '''
    まずは普通のKoch island。
    角度は指定できる。
    '''
    t = ttl.MyTurtle()
    t.tracer(0)
    t.speed(10)

    for i in range(3):
        koch_angle(t, n, length, theta)
        t.right(120)

    t.penup()
    t.save_as_svg('koch_island_test0.svg')
    t.update()
    return t


def test1(n=4, length=200):
    '''
    -60度から60度まで、1度刻みで Koch Island する。
    '''
    t = ttl.MyTurtle()
    t.tracer(0)
    t.speed(10)

    for theta in range(-60, 60):
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)

    t.penup()
    t.save_as_svg('koch_island_test1.svg')
    t.update()
    return t


def test2(n=4, length=200, theta_min=-60, theta_max=60, theta_step=1):
    '''
    test1から、角度の下限、上限、刻みを指定できるように変更した
    '''
    t = ttl.MyTurtle()
    t.tracer(0)
    t.speed(10)

    for theta in range(theta_min, theta_max, theta_step):
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)

    t.penup()
    t.save_as_svg('koch_island_test2.svg')
    t.update()
    return t


def test3(n=4, length=200, theta_min=60, theta_max=-60, theta_step=-1):
    '''
    塗り色を変えながら、外側から内側に向けて塗る例。
    '''
    t = ttl.MyTurtle()
    t.tracer(0)
    t.speed(10)
    
    colors = ["#FF0000", "#FF7700", "#FFFF00", "#77FF00", "#00FF00", 
              "#007700", "#007777", "#0077FF", "#0000FF", "#7700FF", 
              "#770077", "#FF0077"]
    t.penup()
    
    for theta in range(theta_min, theta_max, theta_step):
        t.fillcolor(colors[int(abs(theta)/4) % 12])
        t.begin_fill()
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)
        t.end_fill()

    t.penup()
    t.save_as_svg('koch_island_test3.svg')
    t.update()
    return t


def test4(t=None, n=4, length=200, theta_min=-60, theta_max=60, theta_step=1):
    '''
    線色を変えていき、疑似的にグラデーションする（隙間はできる）
    '''
    t = ttl.MyTurtle()
    t.tracer(0)
    t.speed(10)
    
    colors = ["#ff0000", "#ff7700", "#ffff00", "#77ff00", "#00ff00", 
              "#007700", "#007777", "#0077ff", "#0000ff", "#7700ff", 
              "#770077", "#ff0077"]
    
    t.bgcolor('black')
    
    for theta in range(theta_min, theta_max, theta_step):
        t.pendown()
        color = colors[int(abs(theta)/4) % 12]
        t.pencolor(color)
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)
        t.penup()

    t.penup()
    t.save_as_svg('koch_island_test4.svg')
    t.update()
    return t


def test5(t=None, n=5, length=400, theta_max=60, theta_step=1):
    '''
    -67 <= theta_max <= 60 でないとエラーになるので注意（色の設定のしかたが固定なので）
    
    外側、内側それぞれから、正三角形の方向に向かって塗る。
    塗り色をRGBで徐々に変化させて疑似グラデーション
    '''
    if t is None:
        t = ttl.MyTurtle()
        t.tracer(0)
        t.speed(10)
    
    t.penup()
    
    # 外側
    for theta in range(theta_max, 0, -theta_step):
        R = (135 + theta*2) / 255
        G = (195 + theta) / 255
        B = 255 / 255
        t.fillcolor(R, G, B)
        t.begin_fill()
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)
            
        # 正三角形を描いて図形を閉じる
        t.right(60)
        for i in range(3):
            t.fd(length)
            t.left(120)
        t.left(60)
        t.end_fill()

    # 内側
    for theta in range(-theta_max, 1, theta_step):
        R = (135 + theta*2) / 255
        G = (195 + theta) / 255
        B = 255 / 255
        t.fillcolor(R, G, B)
        t.begin_fill()
        for i in range(3):
            koch_angle(t, n, length, theta)
            t.right(120)
            
        # 正三角形を描いて図形を閉じる
        t.right(60)
        for i in range(3):
            t.fd(length)
            t.left(120)
        t.left(60)
        t.end_fill()

    # 一番外側の輪郭を描く
    t.pendown()
    R = (135 - 60*2) / 255
    G = (195 - 60) / 255
    B = 255 / 255
    t.pencolor(R, G, B)
    for i in range(3):
        koch_angle(t, n, length, 60)
        t.right(120)           

    t.penup()
    t.save_as_svg('koch_island_test5.svg')
    t.update()
    return t

#-- 以下、テスト実行例             -----------------------------------
#-- コメントアウトを1行はずして実行せよ -----------------------------------

#t = test0()
#t = test0(theta=80)
#t = test0(theta=40)
#t = test0(theta=-60)
#t = test1()
#t = test2(theta_min=10, theta_max=61, theta_step=10)
#t = test2(theta_min=-60, theta_max=0, theta_step=10)
#t = test2(theta_min=-60, theta_max=61, theta_step=10)
#t = test2(theta_min=-50, theta_max=80, theta_step=5)
#t = test3()
t = test4()
#t = test5()

