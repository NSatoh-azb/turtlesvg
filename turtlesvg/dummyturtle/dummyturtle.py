"""
@author: NSatoh
Azabu high school, department of mathematics
"""

import math
import copy
from turtle import Vec2D

def dcos(a):
    return math.cos(math.radians(a))

def dsin(a):
    return math.sin(math.radians(a))


class Turtle:

    def __init__(self):
        self._head = 0.0
        self._x = 0.0
        self._y = 0.0
        self._pen = {
                'fillcolor'    : 'black',
                'outline'      : 1,
                'pencolor'     : 'black',
                'pendown'      : True,
                'pensize'      : 1,
                'resizemode'   : 'noresize',
                'shearfactor'  : 0.0,
                'shown'        : True,
                'speed'        : 3,
                'stretchfactor': (1.0, 1.0),
                'tilt'         : 0.0
        }
        self._isdown = True
        self._filling = False
        self.screen = Screen()
   
    def forward(self, d):
        dx = d * dcos(self._head)
        dy = d * dsin(self._head)
        self._x += dx
        self._y += dy
        
    fd = forward
 
    
    def backward(self, d):
        dx = d * dcos(self._head)
        dy = d * dsin(self._head)
        self._x -= dx
        self._y -= dy
        
    bk = backward
    back = backward

    def right(self, a):
        self._head -= a
    rt = right


    def left(self, a):
        self._head += a
    lt = left
    
    def setposition(self, x, y=None):
        '''
        Arguments:
          x -- a number      or     a pair/vector of numbers
          y -- a number             None
    
          call: goto(x, y)         # two coordinates
          --or: goto((x, y))       # a pair (tuple) of coordinates
          --or: goto(vec)          # e.g. as returned by pos()
        '''
        if y is not None:
            self._x = x
            self._y = y
        else:
            self._x = x[0]
            self._y = x[1]
    
    setpos = setposition
    goto = setposition
    
    def setx(self, x):
        self._x = x
    
    def sety(self, y):
        self._y = y

    def setheading(self, a):
        self._head = a    
    seth = setheading

    
    def home(self):
        self._head = 0.0
        self._x = 0.0
        self._y = 0.0
        

    def circle(self, r, extent, steps=None):
        '''
        dummy turtle は実際に途中経過の多角形の頂点を
        計算する必要がないため，移動後の点に座標を変更するのみ．

        半径 r の円弧を，中心角 extent度だけ描く．
        中心はタートルの左90度方向に距離rの点．
　　　　　　　円は内接する正steps角形で近似される．
　　　　　　　extent, stepsは省略可能．
        '''
        if extent:
            # extentの省略は全円を描くため，移動すらない
            cx = self._x + r * dcos(self._head + 90)
            cy = self._y + r * dsin(self._head + 90)
            dx = r * dcos(self._head - 90 + extent)
            dy = r * dsin(self._head - 90 + extent)
            self._x = cx + dx
            self._y = cy + dy
            self._head += extent

    def pendown(self):
        self._isdown = True
    
    pd = pendown 
    down = pendown

    def penup(self):
        self._isdown = False
    pu = penup
    up = penup
    
    def isdown(self):
        return self._isdown



    def pensize(self, w=None):
        if w is not None:
            self._pen['pensize'] = w
        else:
            return self._pen['pensize']

    width = pensize
    
    def pencolor(self, *args):
        '''
        colorstringの処理はsvgutlに投げることにして，
        単に入力された引数をそのまま記録する．
        '''
        if args is ():
            return self._pen['pencolor']
        else:
            self._pen['pencolor'] = _color_format(args)

    def pen(self, pen=None, **pendict):
        if (pen is None) and (pendict == {}):
            return copy.deepcopy(self._pen)
        elif pen is not None:
            self._pen = pen
        else:
            for key in pendict:
                self._pen[key] = pendict[key]
            
        
        
    def begin_fill(self):
        self._filling = True
    
    def end_fill(self):
        self._filling = False

    def filling(self):
        return self._filling

    def fillcolor(self, *args):
        if args == ():
            return self._pen['fillcolor']
        else:
            self._pen['fillcolor'] = _color_format(args)

    
    def undo(self):
        print('undo は 未実装')

    def speed(self, s):
        pass
    def tracer(self, n):
        pass
    
    def update(self):    
        pass
    
    def reset(self):
        self.__init__()

    def clear(self):
        '''
        描いたものを全て消去する．タートルやペンの状態はそのまま．

        '''
        pass

    def hideturtle(self):
        pass
    
    ht = hideturtle
    
    def showturtle(self):
        pass
    
    st = showturtle
        
    def screensize(w,h):
        pass

    def position(self):
        '''
        タートルの現在位置を座標の組（タプル）で返す
        （正確には，\verb|Vec2D|クラスのベクトルオブジェクトとして返す）． 
        '''
        return Vec2D(self._x, self._y)
    
    pos = position
    
    def xcor(self):
        '''
        タートルの現在位置の$x$座標を返す． 
        '''
        return self._x

    def ycor(self):
        '''
        タートルの現在位置の$y$座標を返す．
        '''
        return self._y
    
    def heading(self):
        '''
        タートルの現在の向き（角度）を返す．
        '''
        return self._head
    
    def towards(self, x, y):
        '''
        タートルの現在位置から座標 (x, y) へ向かう角度を返す． 
        '''
        vx = x - self._x
        vy = y - self._y
        # (1, 0)との内積で角度を計算
        angle = math.degrees(math.acos(vx / (vx**2 + vy**2)**0.5))
        if vy < 0:
            return 360 - angle
        else:
            return angle


    def distance(self, x, y):
        '''
        タートルの現在位置から座標(x, y)までの距離を返す． 
        '''
        vx = x - self._x
        vy = y - self._y
        return (vx**2 + vy**2)**0.5
    

    def dot(self, size=None, *color):
        pass


class Screen:
    
    def __init__(self):
        self._bgcolor = 'white'
   
    def tracer(self, n, delay):
        pass
    
    def bgcolor(self, *args):
        if args == ():
            return self._bgcolor
        else:
            self._bgcolor = _color_format(args)
    
    def clearscreen(self):
        pass
    
    def update(self):
        pass


def _color_format(args):
    if type(args) == tuple:
        if len(args) == 1:
            return args[0]
        else:
            return args
    else:
        return args


def update():
    pass