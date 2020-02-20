import turtle
import svgutl.svgutl as svg
import datetime
import math
import copy

class Turtle():
    '''
　　  spyderなど、IPython環境では、マジックコマンド
    
  　    %gui tk
       
  　　を実行してから利用する。（そうしないと動作が不安定）
    
  　　-+-+- 使い方 -+-+-
    
      　　import trutlesvg as ttl
      　　t = ttl.Turtle()
      
    　　として、Turtleオブジェクト t を生成する。
   　　 以下、
      
     　　 t.forward(100)
     　　 t.left(90)
     　　 t.forward(150)
       　   :
        　  :
    
    　　のように、通常のturtleモジュール同様に利用して
    　　タートルを動かして絵を描く。
    　　（ただし、通常のturtleモジュールの全ての機能をサポートしていない・・・！）
      
    　　最後に、
      
      　　t.save_as_svg("filename.svg")
        
    　　などとすると、"filename.svg"にSVGファイルが保存される。  
      
    -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        
    各関数のコメントは，タートルグラフィックスの日本語リファレンス：
      Python >> Documentation >> Python 標準ライブラリ >> 24. プログラムのフレームワーク >>
        24.1. turtle Turtle graphics
      http://docs.python.jp/3.3/library/turtle.html
    による．
    '''
    
    # 亀インスタンスたちには，自身を丸ごと変数に登録させる．
    # cloneしまくって絵を描いたときのcanvas全体を描画したい場合用．
    __turtles_container = []
    __whole_x_min = 0
    __whole_x_max = 0
    __whole_y_min = 0
    __whole_y_max = 0

    def __init__(self):

        self.__turtle = turtle.Turtle()
        self.__turtle.home()

        self._position = self.__turtle.position()
        self._heading  = self.__turtle.heading()

        #tikz用にpolylineを生き残らせている
        #TODO 将来的にはpolylineは削除したい
        self.__polylines = []
        self._polyline_init()
        
        # 線のみをpathで，塗りのみをfill_pathで，独立に管理
        # 従って，pendownかつfillingのときには両方に点を追加していく
        self.__paths = []
        self.__fill_paths = []
        self.__path_recording = False # 記録中はTrueにする．記録中断用．
        self._path_init()
        
        # SVG描画の順番をタートルと同じにするための変数
        self.__faithful_paths = []
        # copyでインスタンス作られるとコンテナ格納が実行されないが，まあもうそれは対応しなくていいよな．
        self.__registrate_to_container()
        # 塗りがある場合は先にfillをやらないと線の上から塗られてしまうので，
        # pathは一時退避させておき，faithful_pathsにはfillが格納されたあとでまとめて格納する．
        # pensize や pencolor の変更があると（fillpathは継続したまま）
        # 複数のpathが退避されることがあるのでリストになっている．
        self.__paths_stashbox = []
        self.__faithful = True # デフォルトはタートルと同じにしておく．

        # dot管理用
        self.circles = Circles()

        self.__x_min = 0
        self.__x_max = 0
        self.__y_min = 0
        self.__y_max = 0

        self.back_ground_color = None

    def set_turtle(self, turtle):
        self.__turtle = turtle

    def get_turtle(self):
        return self.__turtle
    
    def __registrate_to_container(self):
        if self not in self.__turtles_container:
            # 自己を自分のコンテナに内包・・・見た目が恐ろしいな！
            self.__turtles_container.append(self)

    def set_faithful(self, faithful=None):
        '''
        SVG描画順序を，タートルに忠実にするかどうか設定．
        引数なしで呼び出した場合はtoggleする．
        '''
        if faithful is None:
            self.__faithful = not self.__faithful
        else:
            # faithfulがBoolでない場合を想定したコードか？
            # 意図がわからんので__faithful = faithfulに変更するかも
            if faithful:
                self.__faithful = True
            else:
                self.__faithful = False

    def _on_move(self):

        if self.isdown():
            self.__polyline.push_point(self.pos())
            self.__path.append_line_to(self.pos())
            self._update_canvas_size()

        if self.filling():
            # penのUp/Down状態は関係ない
            self.__fill_path.append_line_to(self.pos())
            self._update_canvas_size()

    def _polyline_init(self):
        self.__polyline = Polyline(self.pos())

    def _path_init(self):
        self.__path_recording = True
        self.__path = Path(self.pos())

    def _fill_path_init(self):
        self.__fill_path = Path(self.pos(), filling=True)
        self.__paths_stashbox = []

        
    def _polyline_terminate(self):
        '''
        polylineの記録を終了．
        現在のペン状態をPolylineオブジェクトに記憶させたのち，
        Polylineオブジェクトをリストの末尾に格納する．
        '''
        self.__polyline.set_pen(self.pen())
        self.__polylines.append(self.__polyline)
        self.__polyline = None


    def _path_terminate(self):
        '''
        pathの記録を終了．
        現在のペン状態をPathオブジェクトに記憶させたのち，
        Pathオブジェクトをリストの末尾に格納する．
        格納が行われた場合は，__path はNoneに戻る．
        #TODO Noneになっていなければ格納されていない（移動ナシ判定）
              と判断できるようになっており，実際それが利用されているが，この仕様はなんとかならんものか．
        '''
        # 移動してない場合はリストに追加しない
        if self.__path.was_moved():
            self.__path.set_pen(self.pen())
            self.__paths.append(self.__path)
            if self.filling():
                # 先にfillが格納されるまでpathは一時退避．
                self.__paths_stashbox.append(self.__path)
            else:
                self.__faithful_paths.append(self.__path)
            # Noneになるのは移動している場合のみ
            self.__path = None
        self.__path_recording = False


    def _fill_path_terminate(self):
        # 基本的には
        self.__fill_path.set_pen(self.pen())
        
        # 開始点と終了点をつなぐ（SVGのpath末尾に'Z'をつける）
        # この処理はfillのみ（線の方は閉じない）
        self.__fill_path.close_path()
        self.__fill_paths.append(self.__fill_path)
        
        self.__faithful_paths.append(self.__fill_path)
        self.__faithful_paths += self.__paths_stashbox


    def _restore_polyline(self):
        self.__polyline = self.__polylines.pop()

    def _restore_path(self):
        '''
        現状は，_path_terminate の直後に復元したい場合を想定した機能．
        undoを実装する場合も使えるとは思っている．
        '''
        self.__path = self.__paths.pop()
        # faithful側の復元
        if self.__paths_stashbox[-1] == self.__path:
            self.__paths_stashbox.pop()
        if self.__faithful_paths[-1] == self.__path:
            self.__faithful_paths.pop()
        # 記録再開
        self.__path_recording = True


    def _restore_fill_path(self):
        '''
        今のところこれを利用する予定がないが，将来もしundoを実装する場合は必要か．
        '''
        self.__fill_path = self.__fill_paths.pop()

    #TODO 名前がよくないのでは・・・？
    def _clear_pictures(self):
        self.__polylines = []
        self.__paths = []
        self.__fill_paths = []
        self.__faithful_paths = []
        self.__paths_stashbox = []
        self._polyline_init()
        self._path_init()


    def get_polylines(self):
        return self.__polylines
    
    def get_paths(self):
        return self.__paths

    def get_fill_paths(self):
        return self.__fill_paths

    def get_canvas_size(self):
        return (self.__x_min, self.__x_max, self.__y_min, self.__y_max)

    def _update_canvas_size(self, line_width=None):
        if line_width is None:
            line_width = self.__turtle.pensize()
        (x, y) = self.pos()
        if x - line_width < self.__x_min:
            self.__x_min = x - line_width
            Turtle.__whole_x_min = min(self.__x_min, Turtle.__whole_x_min)
        elif x + line_width  > self.__x_max:
            self.__x_max = x + line_width 
            Turtle.__whole_x_max = max(self.__x_max, Turtle.__whole_x_max)

        if y - line_width  < self.__y_min:
            self.__y_min = y - line_width 
            Turtle.__whole_y_min = min(self.__y_min, Turtle.__whole_y_min)
        elif y + line_width  > self.__y_max:
            self.__y_max = y + line_width 
            Turtle.__whole_y_max = max(self.__y_max, Turtle.__whole_y_max)

    def _set_bgcolor(self, color):
        self.back_ground_color = color


    def save_whole_as_svg(self, filename=None, 
                 unit_width=1, unit_length=1, margin=5, 
                 bg_color=None):
        '''
        すべての亀の描画結果を，1つのSVG画像として保存する．
        
        :param filename:    ファイル名
        :param unit_width:  線の太さ
        :param unit_length: 単位長さ
        :param margin:      画像外周の余白幅
        :param bg_color:    背景色
        
        ・ファイル名を指定せず実行すると，
         「turtlesvg_output_日付時刻.svg」に保存
        ・背景色を設定すると，その色のrectを1つ背後に配置． 
        '''
                
        x0 = int(Turtle.__whole_x_min - margin)
        y0 = int(Turtle.__whole_y_max + margin)
        w = int(Turtle.__whole_x_max + margin*2) - x0
        h = y0 - int(Turtle.__whole_y_min - margin)

        # y座標は反転        
        svg_svg = svg.Svg(w=w, h=h, x0=x0, y0=-y0, vb_w=w, vb_h=h)
        
        # 背景色指定があれば、その色のrectを生成
        if not bg_color and self.back_ground_color:
            bg_color = self.back_ground_color
        if bg_color:
            bg_rect = svg.SvgElement('rect', {
                    'x'      : x0, 
                    'y'      : -y0, 
                    'width'  : w, 
                    'height' : h,
                    'fill'   : bg_color
                    })
            svg_svg.append_element(bg_rect)

        for ttl in self.__turtles_container:
            ttl.__gen_svg_body(svg_svg=svg_svg, unit_width=unit_width, 
                               unit_length=unit_length, margin=margin)

        svg_str = svg_svg.get_svg()
        
        if filename == None:
            dt = datetime.date.today()
            time_str = dt.strftime("%Y-%m%d-%H%M-%S")
            filename = f'turtlesvg_output_{time_str}.svg'
        
        with open(filename, "w") as f:
            f.write(svg_str)


    def save_as_svg(self, filename=None, 
                 unit_width=1, unit_length=1, margin=5, 
                 bg_color=None):
        '''
        タートルグラフィックスの実行結果を，SVG画像として保存する．
        
        :param filename:    ファイル名
        :param unit_width:  線の太さ
        :param unit_length: 単位長さ
        :param margin:      画像外周の余白幅
        :param bg_color:    背景色
        
        ・ファイル名を指定せず実行すると，
         「turtlesvg_output_日付時刻.svg」に保存
        ・背景色を設定すると，その色のrectを1つ背後に配置． 
        '''
                
        x0 = int(self.__x_min - margin)
        y0 = int(self.__y_max + margin)
        w = int(self.__x_max + margin*2) - x0
        h = y0 - int(self.__y_min - margin)

        # y座標は反転        
        svg_svg = svg.Svg(w=w, h=h, x0=x0, y0=-y0, vb_w=w, vb_h=h)
        
        # 背景色指定があれば、その色のrectを生成
        if not bg_color and self.back_ground_color:
            bg_color = self.back_ground_color
        if bg_color:
            bg_rect = svg.SvgElement('rect', {
                    'x'      : x0, 
                    'y'      : -y0, 
                    'width'  : w, 
                    'height' : h,
                    'fill'   : bg_color
                    })
            svg_svg.append_element(bg_rect)
        
        self.__gen_svg_body(svg_svg=svg_svg, unit_width=unit_width, 
                            unit_length=unit_length, margin=margin)

        svg_str = svg_svg.get_svg()
        
        if filename == None:
            dt = datetime.date.today()
            time_str = dt.strftime("%Y-%m%d-%H%M-%S")
            filename = f'turtlesvg_output_{time_str}.svg'
        
        with open(filename, "w") as f:
            f.write(svg_str)



    def __gen_svg_body(self, svg_svg, 
                       unit_width, unit_length, margin):
        '''
        :param svg_svg: svg.Svg object
        svg_svg に，亀の移動結果をsvg化して格納する（return ナシ）
        '''

        # pathが記録中の状態なら一度記録終了させてあとで復元する．
        if self.__path_recording: 
            self._polyline_terminate()
            self._path_terminate()
            restore_flag = True
        else:
            restore_flag = False

        if self.__faithful:
            for ffp in self.__faithful_paths:
                svg_elem = ffp.get_svg(unit_width=unit_width, unit_length=unit_length)
                svg_svg.append_element(svg_elem)
        else:
            # fillが先
            for fp in self.__fill_paths:
                svg_elem = fp.get_svg(unit_width=unit_width, unit_length=unit_length)
                svg_svg.append_element(svg_elem)
    
            for p in self.__paths:
                svg_elem = p.get_svg(unit_width=unit_width, unit_length=unit_length)
                svg_svg.append_element(svg_elem)
    
            #for pl in self.__polylines:
            #    svg_elem = pl.get_svg(unit_width=unit_width, unit_length=unit_length)
            #    svg_svg.append_element(svg_elem)

        #TODO dotによる描画は，他のpathとの順番が記録できていないので，
        #     この実装では faithfulオプションで変化しない．
        svg_circles = svg.SvgCircles(self.circles)
        svg_svg.append_element_str(svg_circles.get_svg())
        
        # pathの記録中だった場合はここで復元
        if restore_flag:
            self._restore_polyline()
            if self.__path is None:
                self._restore_path()
            # うーん．_restore_path内でもTrueにするんだが・・・，
            # 上のif通ってないときのために必要なんだよなあ．
            self.__path_recording = True

            
    def printbb(self):
        print(f"x_min:{self.__x_min}, y_min:{self.__y_min}")
        print(f"x_max:{self.__x_max}, y_max:{self.__y_max}")

    # -- 以下はturtleモジュールから取り込んだ関数たち ---------------------------------------------------

    def forward(self, distance):
        '''
        :param distance : a number (integer or float)
        タートルが頭を向けている方へ、タートルを距離 distance だけ前進させます。

        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.forward(25)
        >>> turtle.position()
        (25.00,0.00)
        >>> turtle.forward(-75)
        >>> turtle.position()
        (-50.00,0.00)
        '''
        self.__turtle.forward(distance)
        self._on_move()

    fd = forward



    def back(self, distance):
        '''
        :param distance : a number
        タートルが頭を向けている方と反対方向へ、タートルを距離 distance だけ後退させます。
        タートルの向きは変えません。

        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.backward(30)
        >>> turtle.position()
        (-30.00,0.00)
        '''
        self.__turtle.backward(distance)
        self._on_move()

    bk = back
    backward = back



    def right(self, angle):
        '''
        :param angle : a number (integer or float)
        タートルを angle 単位だけ右に回します。
        (単位のデフォルトは度ですが、 degrees() と radians() 関数を使って設定できます。)
         角度の向きはタートルのモードによって意味が変わります。 mode() を参照してください。

        >>> turtle.heading()
        22.0
        >>> turtle.right(45)
        >>> turtle.heading()
        337.0
        '''
        self.__turtle.right(angle)

    rt = right



    def left(self, angle):
        '''
        :param angle : a number (integer or float)
        タートルを angle 単位だけ左に回します。
        (単位のデフォルトは度ですが、 degrees() と radians() 関数を使って設定できます。)
         角度の向きはタートルのモードによって意味が変わります。 mode() を参照してください。

        >>> turtle.heading()
        22.0
        >>> turtle.left(45)
        >>> turtle.heading()
        67.0
        '''
        self.__turtle.left(angle)

    lt = left



    def goto(self, x, y=None):
        '''
        :param x : a number or a pair/vector of numbers
        :param y : a number or None
        y が None の場合、 x は座標のペアかまたは Vec2D (たとえば pos() で返されます)
        でなければなりません。

        タートルを指定された絶対位置に移動します。ペンが下りていれば線を引きます。
        タートルの向きは変わりません。

        >>> tp = turtle.pos()
        >>> tp
        (0.00,0.00)
        >>> turtle.setpos(60,30)
        >>> turtle.pos()
        (60.00,30.00)
        >>> turtle.setpos((20,80))
        >>> turtle.pos()
        (20.00,80.00)
        >>> turtle.setpos(tp)
        >>> turtle.pos()
        (0.00,0.00)
        '''
        self.__turtle.setposition(x, y)
        self._on_move()

    setpos = goto
    setposition = goto


    def setx(self, x):
        '''
        :param x : a number (integer or float)
        タートルの第一座標を x にします。第二座標は変わりません。

        >>> turtle.position()
        (0.00,240.00)
        >>> turtle.setx(10)
        >>> turtle.position()
        (10.00,240.00)
        '''
        self.__turtle.setx(x)
        self._on_move()


    def sety(self, y):
        '''
        :param y : a number (integer or float)
        タートルの第二座標を y にします。第一座標は変わりません。

        >>> turtle.position()
        (0.00,40.00)
        >>> turtle.sety(-10)
        >>> turtle.position()
        (0.00,-10.00)
        '''
        self.__turtle.sety(y)
        self._on_move()


    def setheading(self, to_angle):
        '''
        :param to_angle : a number (integer or float)
        タートルの向きを to_angle に設定します。以下はよく使われる方向を度で表わしたものです:

        標準モード
        logo モード
        0 - 東
        0 - 北
        90 - 北
        90 - 東
        180 - 西
        180 - 南
        270 - 南
        270 - 西
        >>> turtle.setheading(90)
        >>> turtle.heading()
        90.0
        '''
        self.__turtle.setheading(to_angle)

    seth = setheading



    def home(self):
        '''
        タートルを原点（座標 (0, 0) ）に移動し、向きを開始方向に設定します
        (開始方向はモードに依って違います。 mode() を参照してください)。

        >>> turtle.heading()
        90.0
        >>> turtle.position()
        (0.00,-10.00)
        >>> turtle.home()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0
        '''
        self.__turtle.home()
        self._on_move()



    def circle(self, radius, extent=None, steps=None):
        '''
        :param radius : a number
        :param extent : a number (or None)
        :param steps : an integer (or None)
        半径 radius の円を描きます。中心はタートルの左 radius ユニットの点です。
        extent（角度です）は円のどの部分を描くかを決定します。
        extent が与えられなければ、デフォルトで完全な円になります。
        extent が完全な円でない場合は、弧の一つの端点は、現在のペンの位置です。
        radius が正の場合、弧は反時計回りに描かれます。そうでなければ、時計回りです。
        最後にタートルの向きが extent 分だけ変わります。

        円は内接する正多角形で近似されます。 steps でそのために使うステップ数を決定します。
        この値は与えられなければ自動的に計算されます。また、これを正多角形の描画に利用する
        こともできます。

        >>> turtle.home()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0
        >>> turtle.circle(50)
        >>> turtle.position()
        (-0.00,0.00)
        >>> turtle.heading()
        0.0
        >>> turtle.circle(120, 180)  # draw a semicircle
        >>> turtle.position()
        (0.00,240.00)
        >>> turtle.heading()
        180.0
        '''
        if not steps: # 正確な全円または円弧の場合        
            
            if extent and abs(extent) < 360: # 円弧
                self.__turtle.circle(radius, extent)
                pt = self.pos()
                
                if abs(extent) < 180:
                    large_arc_flag = 0
                else:
                    large_arc_flag = 1

                if extent < 0 and radius > 0:
                    sweep_flag = 1
                elif extent > 0 and radius < 0:
                    sweep_flag = 1
                else:
                    sweep_flag = 0
                
                self._on_arc_move(abs(radius), abs(radius), 
                                  0, large_arc_flag, sweep_flag,
                                  pt[0], pt[1])
            else: # 全円以上は，半円以下を繰り返し描かせる
                if extent is None:
                    extent = 360

                # 符号判断しないと無限ループするだろ，という渡辺さんの指摘・・・！
                if extent < 0:
                    sgn = -1
                else:
                    sgn = 1
                self.circle(radius, 180*sgn)
                self.circle(radius, extent - 180*sgn)

        else: # 多角形近似の場合
            d_angle = abs(extent) / steps
            l = 2*radius * math.sin(math.radians(d_angle))
            for i in range(steps):
                self.left(d_angle)
                self.forward(l)
            
        
    def _on_arc_move(self, rx, ry, start, f1, f2, x, y):
        if self.isdown():
            self.__path.append_arc(rx, ry, start, f1, f2, x, y)
            # 弧の途中の点でcanvas_sizeが補正されないので，はみ出すかも．
            self._update_canvas_size()

        if self.filling():
            # penのUp/Down状態は関係ない
            self.__fill_path.append_arc(rx, ry, start, f1, f2, x, y)
            self._update_canvas_size()



    def dot(self, size=None, *color):
        '''
        :param size : an integer >= 1 (if given)
        :param color : a colorstring or a numeric color tuple
        直径 size の丸い点を color で指定された色で描きます。 size が与えられなかった場合、
        pensize+4 と 2*pensize の大きい方が使われます。

        >>> turtle.home()
        >>> turtle.dot()
        >>> turtle.fd(50); turtle.dot(20, "blue"); turtle.fd(50)
        >>> turtle.position()
        (100.00,-0.00)
        >>> turtle.heading()
        0.0
        '''
        self.__turtle.dot(size, *color)
        
        if size is None:
            ps = self.__turtle.pensize()
            size = max(ps+4, 2*ps)
        
        # 空なら pencolorの取得は必要だが，rgb変換は
        # 本来 svgutl 側にやらせるべきか（タートル自身の動作が重くなる可能性があるので）
        if color == ():
            c = self.__turtle.pencolor()
            if type(c) is tuple:
                [r, g, b] = [int(c[i]*255) for i in range(3)] 
                c = f'#{r:0>2x}{g:0>2x}{b:0>2x}'
        elif len(color) == 3:
            [r, g, b] = [int(color[i]*255) for i in range(3)] 
            c = f'#{r:0>2x}{g:0>2x}{b:0>2x}'
        else:
            c = color[0]
            
        p = self.__turtle.pos()
        self.circles.append_circle((p[0], p[1], size, c))
        self._update_canvas_size(size)


    def stamp(self):
        '''
        キャンバス上の現在タートルがいる位置にタートルの姿のハンコを押します。
        そのハンコに対して stamp_id が返されますが、これを使うと後で clearstamp(stamp_id)
        のように呼び出して消すことができます。

        >>> turtle.color("blue")
        >>> turtle.stamp()
        11
        >>> turtle.fd(50)
        '''
        self.__turtle.stamp()
        print("このコマンドは出力されるSVGファイルには反映されません．")



    def clearstamp(self, stampid):
        '''
        :param stampid : an integer, must be return value of previous stamp() call
        stampid に対応するハンコを消します。

        >>> turtle.position()
        (150.00,-0.00)
        >>> turtle.color("blue")
        >>> astamp = turtle.stamp()
        >>> turtle.fd(50)
        >>> turtle.position()
        (200.00,-0.00)
        >>> turtle.clearstamp(astamp)
        >>> turtle.position()
        (200.00,-0.00)
        '''
        self.__turtle.clearstamp(stampid)



    def clearstamps(self, n=None):
        '''
        :param n : an integer (or None)
        全ての、または最初の/最後の n 個のハンコを消します。 n が None の場合、全てのハンコを消します。
        n が正の場合には最初の n 個、 n が負の場合には最後の n 個を消します。

        >>> for i in range(8):
        ...     turtle.stamp(); turtle.fd(30)
        13
        14
        15
        16
        17
        18
        19
        20
        >>> turtle.clearstamps(2)
        >>> turtle.clearstamps(-2)
        >>> turtle.clearstamps()
        '''
        self.__turtle.clearstamps(n)



    def undo(self):
        '''
        最後の(繰り返すことにより複数の)タートルの動きを取り消します。
        取り消しできる動きの最大数は undobuffer のサイズによって決まります。

        >>> for i in range(4):
        ...     turtle.fd(50); turtle.lt(80)
        ...
        >>> for i in range(8):
        ...     turtle.undo()
        '''
        #TODO: つくる
        # undoは、かなり実装したいのだが、思ってたより大変そうだなこれは・・・
        print("Sorry. This command is unsupported...")



    def speed(self, speed=None):
        '''
        :param speed : an integer in the range 0..10 or a speedstring (see below)
        タートルのスピードを 0 から 10 までの範囲の整数に設定します。
        引数が与えられない場合は現在のスピードを返します。

        与えられた数字が 10 より大きかったり 0.5 より小さかったりした場合は、
        スピードは 0 になります。スピードを表わす文字列は次のように数字に変換されます:

        "fastest": 0
        "fast": 10
        "normal": 6
        "slow": 3
        "slowest": 1
        1 から 10 までのスピードを上げていくにつれて線を描いたりタートルが回ったりする
        アニメーションがだんだん速くなります。

        注意: speed = 0 はアニメーションを無くします。 forward/backward ではタートルがジャンプし、
        left/right では瞬時に方向を変えます。

        >>> turtle.speed()
        3
        >>> turtle.speed('normal')
        >>> turtle.speed()
        6
        >>> turtle.speed(9)
        >>> turtle.speed()
        9
        '''
        return self.__turtle.speed(speed)



    def position(self):
        '''
        タートルの現在位置を (Vec2D のベクトルとして) 返します。

        >>> turtle.pos()
        (440.00,-0.00)
        '''
        self._position = self.__turtle.position()
        return self._position

    pos = position



    def towards(self, x, y=None):
        '''
        :param x : a number or a pair/vector of numbers or a turtle instance
        :param y : a number if x is a number, else None
        タートルの位置から指定された (x,y) への直線の角度を返します。
        この値はタートルの開始方向にそして開始方向はモード
        ("standard"/"world" または "logo") に依存します。

        >>> turtle.goto(10, 10)
        >>> turtle.towards(0,0)
        225.0
        '''
        return self.__turtle.towards(x, y)



    def xcor(self):
        '''
        タートルの x 座標を返します。

        >>> turtle.home()
        >>> turtle.left(50)
        >>> turtle.forward(100)
        >>> turtle.pos()
        (64.28,76.60)
        >>> print(round(turtle.xcor(), 5))
        64.27876
        '''
        return self.__turtle.xcor()



    def ycor(self):
        '''
        タートルの y 座標を返します。

        >>> turtle.home()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print(turtle.pos())
        (50.00,86.60)
        >>> print(round(turtle.ycor(), 5))
        86.60254
        '''
        return self.__turtle.ycor()



    def heading(self):
        '''
        タートルの現在の向きを返します
        (返される値はタートルのモードに依存します。 mode() を参照してください)。

        >>> turtle.home()
        >>> turtle.left(67)
        >>> turtle.heading()
        67.0
        '''
        return self.__turtle.heading()



    def distance(self, x, y=None):
        '''
        :param x : a number or a pair/vector of numbers or a turtle instance
        :param y : a number if x is a number, else None
        タートルから与えられた (x,y) あるいはベクトルあるいは渡されたタートルへの距離を、
        タートルのステップを単位として測った値を返します。

        >>> turtle.home()
        >>> turtle.distance(30,40)
        50.0
        >>> turtle.distance((30,40))
        50.0
        >>> joe = Turtle()
        >>> joe.forward(77)
        >>> turtle.distance(joe)
        77.0
        24.1.3.3. 設定と計測
        '''
        return self.__turtle.distance(x,y)


    def degrees(self, fullcircle=360.0):
        '''
        :param fullcircle : a number
        角度を計る単位「度」を、円周を何等分するかという値に指定します。
        デフォルトは360等分で通常の意味での度です。

        >>> turtle.home()
        >>> turtle.left(90)
        >>> turtle.heading()
        90.0

        Change angle measurement unit to grad (also known as gon,
        grade, or gradian and equals 1/100-th of the right angle.)
        >>> turtle.degrees(400.0)
        >>> turtle.heading()
        100.0
        >>> turtle.degrees(360)
        >>> turtle.heading()
        90.0
        '''
        return self.__turtle.degrees(fullcircle)


    def radians(self):
        '''
        角度を計る単位をラジアンにします。 degrees(2*math.pi) と同じ意味です。

        >>> turtle.home()
        >>> turtle.left(90)
        >>> turtle.heading()
        90.0
        >>> turtle.radians()
        >>> turtle.heading()
        1.5707963267948966
        24.1.3.4. Pen の制御
        24.1.3.4.1. 描画状態
        '''
        return self.__turtle.radians()



    def pendown(self):
        '''
        ペンを下ろします（動くと線が引かれます）。

        '''
        self.__turtle.pendown()
        self._polyline_init()
        self._path_init()

    pd = pendown
    down = pendown


    def penup(self):
        '''
        ペンを上げます（動いても線は引かれません）。

        '''
        self.__turtle.penup()
        self._polyline_terminate()
        self._path_terminate()

    pu = penup
    up = penup


    def pensize(self, width=None):
        '''
        :param width : a positive number
        線の太さを width にするか、または現在の太さを返します。
        resizemode が "auto" でタートルの形が多角形の場合、その多角形も同じ太さで描画されます。
        引数が渡されなければ、現在の pensize が返されます。

        >>> turtle.pensize()
        1
        >>> turtle.pensize(10)   # from here on lines of width 10 are drawn
        '''
        if width is None:
            return self.__turtle.pensize()

        # width変更があった場合はpolylineを閉じる
        else:            
            if self.isdown():
                self._polyline_terminate()
                self._polyline_init()
                self._path_terminate()
                self._path_init()
            self.__turtle.pensize(width)

    width = pensize



    def pen(self, pen=None, **pendict):
        '''
        :param pen : a dictionary with some or all of the below listed keys
        :param pendict : one or more keyword-arguments with the below listed keys as keywords
        ペンの属性を "pen-dictionary" に以下のキー/値ペアで設定するかまたは返します:

        !!-- この関数に引数を与えて実行すると，変更の有無に関わらず1度polylineは閉じられる --!!

        "shown": True/False
        "pendown": True/False
        "pencolor": 色文字列または色タプル

        "fillcolor": 色文字列または色タプル

        "pensize": 正の数

        "speed": 0 から 10 までの整数

        "resizemode": "auto" または "user" または "noresize"

        "stretchfactor": (正の数, 正の数)

        "outline": 正の数

        "tilt": 数

        この辞書を以降の pen() 呼出しに渡して以前のペンの状態に復旧することができます。
        さらに一つ以上の属性をキーワード引数として渡すこともできます。
        一つの文で幾つものペンの属性を設定するのに使えます。

        >>> turtle.pen(fillcolor="black", pencolor="red", pensize=10)
        >>> sorted(turtle.pen().items())
        [('fillcolor', 'black'), ('outline', 1), ('pencolor', 'red'),
         ('pendown', True), ('pensize', 10), ('resizemode', 'noresize'),
         ('shearfactor', 0.0), ('shown', True), ('speed', 9),
         ('stretchfactor', (1.0, 1.0)), ('tilt', 0.0)]
        >>> penstate=turtle.pen()
        >>> turtle.color("yellow", "")
        >>> turtle.penup()
        >>> sorted(turtle.pen().items())[:3]
        [('fillcolor', ''), ('outline', 1), ('pencolor', 'yellow')]
        >>> turtle.pen(penstate, fillcolor="green")
        >>> sorted(turtle.pen().items())[:3]
        [('fillcolor', 'green'), ('outline', 1), ('pencolor', 'red')]
        '''
        if not (pen or pendict):
            return self.__turtle.pen()

        else:
            self.__turtle.pen(pen=pen, **pendict)

            if self.isdown():
                # 変更が指定されていれば（実際には変わっていない場合でも）polylineを閉じる
                # _polyline_terminate()は，中でこのpen()を呼び出すので，気を付けないと無限ループする．
                # 引数なしでpen()を呼び出すと，上のreturnが実行されるはずなので大丈夫なはず．
                # なんか危ない作り方ではあるな，なんとかならんものかこれ．
                self._polyline_terminate()
                self._polyline_init()


    def isdown(self):
        '''
        もしペンが下りていれば True を、上がっていれば False を返します。

        >>> turtle.penup()
        >>> turtle.isdown()
        False
        >>> turtle.pendown()
        >>> turtle.isdown()
        True
        '''
        return self.__turtle.isdown()



    def pencolor(self, *args):
        '''
        ペンの色(pencolor)を設定するかまたは返します。

        4種類の入力形式が受け入れ可能です:

        pencolor()
        現在のペンの色を色指定文字列またはタプルで返します (例を見て下さい)。
        次の color/pencolor/fillcolor の呼び出しへの入力に使うこともあるでしょう。

        pencolor(colorstring)
        ペンの色を colorstring に設定します。その値は Tk の色指定文字列で、
        "red", "yellow", "#33cc8c" のような文字列です。

        pencolor((r, g, b))
        ペンの色を r, g, b のタプルで表された RGB の色に設定します。
        各 r, g, b は 0 から colormode の間の値でなければなりません。
        ここで colormode は 1.0 か 255 のどちらかです (colormode() を参照)。

        pencolor(r, g, b)
        ペンの色を r, g, b で表された RGB の色に設定します。
        各 r, g, b は 0 から colormode の間の値でなければなりません。

        タートルの形(turtleshape)が多角形の場合、多角形の外側が新しく設定された色で描かれます。

        >>> colormode()
        1.0
        >>> turtle.pencolor()
        'red'
        >>> turtle.pencolor("brown")
        >>> turtle.pencolor()
        'brown'
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.pencolor(tup)
        >>> turtle.pencolor()
        (0.2, 0.8, 0.5490196078431373)
        >>> colormode(255)
        >>> turtle.pencolor()
        (51.0, 204.0, 140.0)
        >>> turtle.pencolor('#32c18f')
        >>> turtle.pencolor()
        (50.0, 193.0, 143.0)
        '''
        if args == ():
            return self.__turtle.pencolor()

        else:
            # 色変更があった場合はpolylineを閉じる
            if self.isdown():
                self._polyline_terminate()
                self._polyline_init()
                self._path_terminate()
                self._path_init()
            self.__turtle.pencolor(*args)



    def fillcolor(self, *args):
        '''
        塗りつぶしの色(fillcolor)を設定するかまたは返します。

        4種類の入力形式が受け入れ可能です:

        fillcolor()
        現在の塗りつぶしの色を色指定文字列またはタプルで返します (例を見て下さい)。
        次の color/pencolor/fillcolor の呼び出しへの入力に使うこともあるでしょう。

        fillcolor(colorstring)
        塗りつぶしの色を colorstring に設定します。その値は Tk の色指定文字列で、
        "red", "yellow", "#33cc8c" のような文字列です。

        fillcolor((r, g, b))
        塗りつぶしの色を r, g, b のタプルで表された RGB の色に設定します。
        各 r, g, b は 0 から colormode の間の値でなければなりません。
        ここで colormode は 1.0 か 255 のどちらかです (colormode() を参照)。

        fillcolor(r, g, b)
        塗りつぶしの色を r, g, b で表された RGB の色に設定します。
        各 r, g, b は 0 から colormode の間の値でなければなりません。

        タートルの形(turtleshape)が多角形の場合、多角形の内側が新しく設定された色で描かれます。

        >>> turtle.fillcolor("violet")
        >>> turtle.fillcolor()
        'violet'
        >>> col = turtle.pencolor()
        >>> col
        (50.0, 193.0, 143.0)
        >>> turtle.fillcolor(col)
        >>> turtle.fillcolor()
        (50.0, 193.0, 143.0)
        >>> turtle.fillcolor('#ffffff')
        >>> turtle.fillcolor()
        (255.0, 255.0, 255.0)
        '''
        return self.__turtle.fillcolor(*args)



    def color(self, *args):
        '''
        ペンの色(pencolor)と塗りつぶしの色(fillcolor)を設定するかまたは返します。

        いくつかの入力形式が受け入れ可能です。
        形式ごとに 0 から 3 個の引数を以下のように使います:

        color()
        現在のペンの色と塗りつぶしの色を pencolor() および fillcolor() で返される色指定文字列
        またはタプルのペアで返します。

        color(colorstring), color((r,g,b)), color(r,g,b)
        pencolor() の入力と同じですが、塗りつぶしの色とペンの色、両方を与えられた値に設定します。

        color(colorstring1, colorstring2), color((r1,g1,b1), (r2,g2,b2))
        pencolor(colorstring1) および fillcolor(colorstring2) を呼び出すのと等価です。
        もう一つの入力形式についても同様です。

        タートルの形(turtleshape)が多角形の場合、多角形の内側も外側も新しく設定された色で描かれます。

        >>> turtle.color("red", "green")
        >>> turtle.color()
        ('red', 'green')
        >>> color("#285078", "#a0c8f0")
        >>> color()
        ((40.0, 80.0, 120.0), (160.0, 200.0, 240.0))
        こちらも参照: スクリーンのメソッド colormode() 。
        '''
        return self.__turtle.color(*args)


    def filling(self):
        '''
        Return fillstate (True if filling, False else).

        >>> turtle.begin_fill()
        >>> if turtle.filling():
        ...    turtle.pensize(5)
        ... else:
        ...    turtle.pensize(3)
        '''
        return self.__turtle.filling()



    def begin_fill(self):
        '''
        To be called just before drawing a shape to be filled.

        '''
        self._fill_path_init()
        self.__turtle.begin_fill()



    def end_fill(self):
        '''
        Fill the shape drawn after the last call to begin_fill().

        >>> turtle.color("black", "red")
        >>> turtle.begin_fill()
        >>> turtle.circle(80)
        >>> turtle.end_fill()
        24.1.3.4.4. さらなる描画の制御
        '''
        self._path_terminate()
        self._fill_path_terminate()
        if self.isdown():
            self._path_init()

        self.__turtle.end_fill()


    def reset(self):
        '''
        タートルの描いたものをスクリーンから消し、タートルを中心に戻して、
        全ての変数をデフォルト値に設定し直します。

        >>> turtle.goto(0,-22)
        >>> turtle.left(100)
        >>> turtle.position()
        (0.00,-22.00)
        >>> turtle.heading()
        100.0
        >>> turtle.reset()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0
        '''
        self.__turtle.reset()
        self._clear_pictures()



    def clear(self):
        '''
        タートルの描いたものをスクリーンから消します。タートルは動かしません。
        タートルの状態と位置、それに他のタートルたちの描いたものは影響を受けません。

        '''
        self.__turtle.clear()
        self._clear_pictures()



    def write(self, arg, move=False, align="left", font=("Arial", 8, "normal")):
        '''
        :param arg : object to be written to the TurtleScreen
        :param move : True/False
        :param align : one of the strings "left", "center" or right"
        :param font : a triple (fontname, fontsize, fonttype)
        Write text - the string representation of arg - at the current turtle position
        according to align ("left", "center" or right") and with the given font. If move is true,
        the pen is moved to the bottom-right corner of the text. By default, move is False.

        >>> turtle.write("Home = ", True, align="center")
        >>> turtle.write((0,0), True)
        '''
        #TODO stringオブジェクトとかを作って対応すればこの機能も使えるようには出来そう．いずれ．
        pass



    def hideturtle(self):
        '''
        タートルを見えなくします。複雑な図を描いている途中、
        タートルが見えないようにするのは良い考えです。
        というのもタートルを隠すことで描画が目に見えて速くなるからです。

        >>> turtle.hideturtle()
        '''
        # 移動後にタートルを隠すことはよくあるので，
        # ここに _path_terminate を仕込んでも良いような予感はするが，保留．
        self.__turtle.hideturtle()

    ht = hideturtle



    def showturtle(self):
        '''
        タートルが見えるようにします。

        >>> turtle.showturtle()
        '''
        self.__turtle.showturtle()

    st = showturtle



    def isvisible(self):
        '''
        Return True if the Turtle is shown, False if it’s hidden.

        >>> turtle.hideturtle()
        >>> turtle.isvisible()
        False
        >>> turtle.showturtle()
        >>> turtle.isvisible()
        True
        '''
        return self.__turtle.isvisible()


# wip ------

    def shape(self, name=None):
        '''
        :param name : a string which is a valid shapename
        タートルの形を与えられた名前(name)の形に設定するか、
        もしくは名前が与えられなければ現在の形の名前を返します。
        name という名前の形は TurtleScreen の形の辞書に載っていなければなりません。
        最初は次の多角形が載っています: "arrow", "turtle", "circle", "square", "triangle", "classic"。
        形についての扱いを学ぶには Screen のメソッド register_shape() を参照して下さい。

        >>> turtle.shape()
        'classic'
        >>> turtle.shape("turtle")
        >>> turtle.shape()
        'turtle'
        '''
        pass



    def resizemode(self, rmode=None):
        '''
        :param rmode : one of the strings "auto", "user", "noresize"
        サイズ変更のモード(resizemode)を "auto", "user", "noresize" のどれかに設定します。
        もし rmode が与えられなければ、現在のサイズ変更モードを返します。
        それぞれのサイズ変更モードは以下の効果を持ちます:

        "auto": ペンのサイズに対応してタートルの見た目を調整します。

        "user": 伸長係数(stretchfactor)およびアウトライン幅(outlinewidth)の値に対応して
        タートルの見た目を調整します。これらの値は shapesize() で設定します。

        "noresize": タートルの見た目を調整しません。

        resizemode("user") は shapesize() に引数を渡したときに呼び出されます。

        >>> turtle.resizemode()
        'noresize'
        >>> turtle.resizemode("auto")
        >>> turtle.resizemode()
        'auto'
        '''
        pass



    def shapesize(self, stretch_wid=None, stretch_len=None, outline=None):
        '''
        :param stretch_wid : positive number
        :param stretch_len : positive number
        :param outline : positive number
        ペンの属性 x/y-伸長係数および/またはアウトラインを返すかまたは設定します。
        サイズ変更のモードは "user" に設定されます。サイズ変更のモードが "user" に
        設定されたときかつそのときに限り、タートルは伸長係数(stretchfactor)に従って伸長されて表示されます。
         stretch_wid は進行方向に直交する向きの伸長係数で、 stretch_len は進行方向に沿ったの伸長係数、
          outline はアウトラインの幅を決めるものです。

        >>> turtle.shapesize()
        (1.0, 1.0, 1)
        >>> turtle.resizemode("user")
        >>> turtle.shapesize(5, 5, 12)
        >>> turtle.shapesize()
        (5, 5, 12)
        >>> turtle.shapesize(outline=8)
        >>> turtle.shapesize()
        (5, 5, 8)
        '''
        pass

    turtlesize = shapesize


    def shearfactor(self, shear=None):
        '''
        :param shear : number (optional)
        Set or return the current shearfactor. Shear the turtleshape according to the given
        shearfactor shear, which is the tangent of the shear angle. Do not change the turtle’s
        heading (direction of movement). If shear is not given: return the current shearfactor,
        i. e. the tangent of the shear angle, by which lines parallel to the heading of the
        turtle are sheared.

        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.shearfactor(0.5)
        >>> turtle.shearfactor()
        0.5
        '''
        pass



    def tilt(self, angle):
        '''
        :param angle : a number
        タートルの形(turtleshape)を現在の傾斜角から角度(angle)だけ回転します。
        このときタートルの進む方向は 変わりません 。

        >>> turtle.reset()
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        '''
        pass



    def settiltangle(self, angle):
        '''
        :param angle : a number
        タートルの形(turtleshape)を現在の傾斜角に関わらず、指定された角度(angle)の向きに回転します。
        タートルの進む方向は 変わりません 。

        >>> turtle.reset()
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.settiltangle(45)
        >>> turtle.fd(50)
        >>> turtle.settiltangle(-45)
        >>> turtle.fd(50)
        バージョン 3.1 で撤廃.
        '''
        pass



    def tiltangle(self, angle=None):
        '''
        :param angle : a number (optional)
        Set or return the current tilt-angle. If angle is given, rotate the turtleshape
        to point in the direction specified by angle, regardless of its current tilt-angle.
        Do not change the turtle’s heading (direction of movement).
        If angle is not given: return the current tilt-angle,
        i. e. the angle between the orientation of the turtleshape and the heading of
        the turtle (its direction of movement).

        >>> turtle.reset()
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(45)
        >>> turtle.tiltangle()
        45.0
        '''
        pass



    def shapetransform(self, t11=None, t12=None, t21=None, t22=None):
        '''
        パラメタ:
        :param t11 : a number (optional)
        :param t12 : a number (optional)
        :param t21 : a number (optional)
        :param t12 : a number (optional)
        Set or return the current transformation matrix of the turtle shape.

        If none of the matrix elements are given, return the transformation matrix
        as a tuple of 4 elements. Otherwise set the given elements and transform
        the turtleshape according to the matrix consisting of first row t11,
        t12 and second row t21, 22. The determinant t11 * t22 - t12 * t21 must not be zero,
        otherwise an error is raised. Modify stretchfactor, shearfactor and tiltangle
        according to the given matrix.

        >>> turtle = Turtle()
        >>> turtle.shape("square")
        >>> turtle.shapesize(4,2)
        >>> turtle.shearfactor(-0.5)
        >>> turtle.shapetransform()
        (4.0, -1.0, -0.0, 2.0)
        '''
        pass



    def get_shapepoly(self):
        '''
        Return the current shape polygon as tuple of coordinate pairs.
        This can be used to define a new shape or components of a compound shape.

        >>> turtle.shape("square")
        >>> turtle.shapetransform(4, -1, 0, 2)
        >>> turtle.get_shapepoly()
        ((50, -20), (30, 20), (-50, 20), (-30, -20))
        '''
        pass



    def onclick(self, fun, btn=1, add=None):
        '''
        :param fun : a function with two arguments which will be called with the coordinates of
                     the clicked point on the canvas
        :param num : number of the mouse-button, defaults to 1 (left mouse button)
        :param add : True or False -- if True, a new binding will be added,
                     otherwise it will replace a former binding
        fun をタートルのマウスクリック(mouse-click)イベントに束縛します。
        fun が None ならば、既存の束縛が取り除かれます。
        無名タートル、つまり手続き的なやり方の例です:

        >>> def turn(x, y):
        ...     left(180)
        ...
        >>> onclick(turn)  # Now clicking into the turtle will turn it.
        >>> onclick(None)  # event-binding will be removed
        '''
        pass



    def onrelease(self, fun, btn=1, add=None):
        '''
        :param fun : a function with two arguments which will be called with the coordinates of
                     the clicked point on the canvas
        :param num : number of the mouse-button, defaults to 1 (left mouse button)
        :param add : True or False -- if True, a new binding will be added, otherwise it will replace
                     a former binding
        fun をタートルのマウスボタンリリース(mouse-button-release)イベントに束縛します。
        fun が None ならば、既存の束縛が取り除かれます。

        >>> class Turtle(Turtle):
        ...     def glow(self,x,y):
        ...         self.fillcolor("red")
        ...     def unglow(self,x,y):
        ...         self.fillcolor("")
        ...
        >>> turtle = Turtle()
        >>> turtle.onclick(turtle.glow)     # clicking on turtle turns fillcolor red,
        >>> turtle.onrelease(turtle.unglow) # releasing turns it to transparent.
        '''
        pass



    def ondrag(self, fun, btn=1, add=None):
        '''
        パラメタ:
        :param fun : a function with two arguments which will be called with the coordinates of
                     the clicked point on the canvas
        :param num : number of the mouse-button, defaults to 1 (left mouse button)
        :param add : True or False -- if True, a new binding will be added, otherwise it will
                     replace a former binding
        fun をタートルのマウスムーブ(mouse-move)イベントに束縛します。
        fun が None ならば、既存の束縛が取り除かれます。

        注意: 全てのマウスムーブイベントのシーケンスに先立ってマウスクリックイベントが起こります。

        >>> turtle.ondrag(turtle.goto)
        この後、タートルをクリックしてドラッグするとタートルはスクリーン上を動きそれによって
        (ペンが下りていれば)手書きの線ができあがります。
        '''
        pass



    def begin_poly(self):
        '''
        多角形の頂点の記録を開始します。現在のタートル位置が最初の頂点です。

        '''
        pass



    def end_poly(self):
        '''
        多角形の頂点の記録を停止します。
        現在のタートル位置が最後の頂点です。
        この頂点が最初の頂点と結ばれます。

        '''
        pass



    def get_poly(self):
        '''
        最後に記録された多角形を返します。

        >>> turtle.home()
        >>> turtle.begin_poly()
        >>> turtle.fd(100)
        >>> turtle.left(20)
        >>> turtle.fd(30)
        >>> turtle.left(60)
        >>> turtle.fd(50)
        >>> turtle.end_poly()
        >>> p = turtle.get_poly()
        >>> register_shape("myFavouriteShape", p)
        '''
        pass



    def clone(self):
        '''
        位置、向きその他のプロパティがそっくり同じタートルのクローンを作って返します。

        >>> mick = Turtle()
        >>> joe = mick.clone()
        
        #TODO: クローンを繰り返し作りながら再帰的に動くような亀を作ると，
               今の実装では1つ1つの亀の持っているpathなどの情報は
               バラバラ（クローン先の亀はもとのpathも持っているが）．
               path のデータを亀に持たせる今のやり方では仕方ない．
               canvas にも記録させるとか，何か全体的な変更が必要．
        
        '''
        t_origin = self.get_turtle()
        t_clone = t_origin.clone()
        # deepcopy回避のために亀への参照を一度切る
        self.set_turtle(None)
        t_new = copy.deepcopy(self)
        
        # 亀戻す
        self.set_turtle(t_origin)
        t_new.set_turtle(t_clone)
        
        # copyで作ったので亀コンテナには未登録
        t_new.__registrate_to_container()
        
        return t_new



    def getturtle(self):
        '''
        Turtle オブジェクトそのものを返します。
        唯一の意味のある使い方: 無名タートルを返す関数として使う:

        >>> pet = getturtle()
        >>> pet.fd(50)
        >>> pet
        <turtle.Turtle object at 0x...>
        '''
        pass

    getpen = getturtle


    def getscreen(self):
        '''
        タートルが描画中の TurtleScreen オブジェクトを返します。
        TurtleScreen のメソッドをそのオブジェクトに対して呼び出すことができます。

        >>> ts = turtle.getscreen()
        >>> ts
        <turtle._Screen object at 0x...>
        >>> ts.bgcolor("pink")
        '''
        pass



    def setundobuffer(self, size):
        '''
        :param size : an integer or None
        アンドゥバッファを設定または無効化します。
        size が整数ならばそのサイズの空のアンドゥバッファを用意します。
        size の値はタートルのアクションを何度 undo() メソッド/関数で取り消せるかの最大数を与えます。
        size が None ならば、アンドゥバッファは無効化されます。

        >>> turtle.setundobuffer(42)
        '''
        pass



    def undobufferentries(self):
        '''
        アンドゥバッファのエントリー数を返します。

        >>> while undobufferentries():
        ...     undo()

        合成されたタートルの形、つまり幾つかの色の違う多角形から成るような形を使うには、
        以下のように補助クラス Shape を直接使わなければなりません:

        タイプ "compound" の空の Shape オブジェクトを作ります。

        addcomponent() メソッドを使って、好きなだけここにコンポーネントを追加します。

        例えば:

        >>> s = Shape("compound")
        >>> poly1 = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s.addcomponent(poly1, "red", "blue")
        >>> poly2 = ((0,0),(10,-5),(-10,-5))
        >>> s.addcomponent(poly2, "blue", "red")
        こうして作った Shape を Screen の形のリスト(shapelist) に追加して使います:
        '''
        pass


    '''
        >>> register_shape("myshape", s)
        >>> shape("myshape")
        注釈 Shape クラスは register_shape() の内部では違った使われ方をします。
        アプリケーションを書く人が Shape クラスを扱わなければならないのは、
        上で示したように合成された形を使うとき だけ です。
    '''

    def bgcolor(self, *args):
        '''
        :param args : a color string or three numbers in the range 0..colormode or a 3-tuple of such numbers
        TurtleScreen の背景色を設定するかまたは返します。

        >>> screen.bgcolor("orange")
        >>> screen.bgcolor()
        'orange'
        >>> screen.bgcolor("#800080")
        >>> screen.bgcolor()
        (128.0, 0.0, 128.0)
        '''
        self.__turtle.screen.bgcolor(*args)
        if args:
            self._set_bgcolor(*args)


    def bgpic(self, picname=None):
        '''
        :param picname : a string, name of a gif-file or "nopic", or None
        背景の画像を設定するかまたは現在の背景画像(backgroundimage)の名前を返します。
        picname がファイル名ならば、その画像を背景に設定します。
        picname が "nopic" ならば、(もしあれば)背景画像を削除します。
        picname が None ならば、現在の背景画像のファイル名を返します。

        >>> screen.bgpic()
        'nopic'
        >>> screen.bgpic("landscape.gif")
        >>> screen.bgpic()
        "landscape.gif"
        '''
        pass



    def clearscreen(self):
        '''
        全ての図形と全てのタートルを TurtleScreen から削除します。
        そして空になった TurtleScreen をリセットして初期状態に戻します:
        白い背景、背景画像もイベント束縛もなく、トレーシングはオンです。

        注釈 この TurtleScreen メソッドはグローバル関数としては clearscreen という名前でだけ使えます。
        グローバル関数 clear は Turtle メソッドの clear から派生した別ものです。
        '''
        self.__turtle.screen.clearscreen()
        self.__init__()



    def resetscreen(self):
        '''
        スクリーン上の全てのタートルをリセットしその初期状態に戻します。

        注釈 この TurtleScreen メソッドはグローバル関数としては resetscreen という名前でだけ使えます。
        グローバル関数 reset は Turtle メソッドの reset から派生した別ものです。
        '''
        pass


    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        '''
        :param canvwidth : positive integer, new width of canvas in pixels
        :param canvheight : positive integer, new height of canvas in pixels
        :param bg : colorstring or color-tuple, new background color
        引数が渡されなければ、現在の (キャンバス幅, キャンバス高さ) を返します。
        そうでなければタートルが描画するキャンバスのサイズを変更します。
        描画ウィンドウには影響しません。
        キャンバスの隠れた部分を見るためにはスクロールバーを使って下さい。
        このメソッドを使うと、以前はキャンバスの外にあったそうした図形の一部を見えるようにすることができます。

        >>> screen.screensize()
        (400, 300)
        >>> screen.screensize(2000,1500)
        >>> screen.screensize()
        (2000, 1500)
        # 逃げ出してしまったタートルを探すためとかね ;-)

        '''
        return self.__turtle.screen.screensize(canvwidth, canvheight, bg)



    def setworldcoordinates(self, llx, lly, urx, ury):
        '''
        :param llx : a number, x-coordinate of lower left corner of canvas
        :param lly : a number, y-coordinate of lower left corner of canvas
        :param urx : a number, x-coordinate of upper right corner of canvas
        :param ury : a number, y-coordinate of upper right corner of canvas
        ユーザー定義座標系を準備し必要ならばモードを "world" に切り替えます。
        この動作は screen.reset() を伴います。
        すでに "world" モードになっていた場合、全ての図形は新しい座標に従って再描画されます。

        重要なお知らせ: ユーザー定義座標系では角度が歪むかもしれません。

        >>> screen.reset()
        >>> screen.setworldcoordinates(-50,-7.5,50,7.5)
        >>> for _ in range(72):
        ...     left(10)
        ...
        >>> for _ in range(8):
        ...     left(45); fd(2)   # a regular octagon
        '''
        pass



    def delay(self, delay=None):
        '''
        :param delay : positive integer
        描画の遅延(delay)をミリ秒単位で設定するかまたはその値を返します。
        (これは概ね引き続くキャンバス更新の時間間隔です。) 遅延が大きくなると、アニメーションは遅くなります。

        オプション引数:

        >>> screen.delay()
        10
        >>> screen.delay(5)
        >>> screen.delay()
        5
        '''
        return self.__turtle.screen.tdelay(delay)



    def tracer(self, n=None, delay=None):
        '''
        :param n : nonnegative integer
        :param delay : nonnegative integer
        Turn turtle animation on/off and set delay for update drawings. If n is given,
        only each n-th regular screen update is really performed.
        (Can be used to accelerate the drawing of complex graphics.)
         When called without arguments, returns the currently stored value of n.
         Second argument sets delay value (see delay()).

        >>> screen.tracer(8, 25)
        >>> dist = 2
        >>> for i in range(200):
        ...     fd(dist)
        ...     rt(90)
        ...     dist += 2
        '''
        # ここは self.__turtle.screen.tracer(n, delay) にすべきか？
        return turtle.tracer(n, delay)



    def update(self):
        '''
        TurtleScreen の更新を実行します。トレーサーがオフの時に使われます。

        RawTurtle/Turtle のメソッド speed() も参照して下さい。
        '''
        turtle.update()



    def listen(self, xdummy=None, ydummy=None):
        '''
        TurtleScreen に(キー・イベントを収集するために)フォーカスします。
        ダミー引数は listen() を onclick メソッドに渡せるようにするためのものです。

        '''
        pass



    def onkey(self, fun, key):
        '''
        パラメタ:
        :param fun : a function with no arguments or None
        :param key : a string: key (e.g. "a") or key-symbol (e.g. "space")
        fun を指定されたキーのキーリリース(key-release)イベントに束縛します。
        fun が None ならばイベント束縛は除かれます。注意: キー・イベントを登録
        できるようにするためには TurtleScreen はフォーカスを持っていないと
        なりません(listen() を参照)。

        >>> def f():
        ...     fd(50)
        ...     lt(60)
        ...
        >>> screen.onkey(f, "Up")
        >>> screen.listen()
        '''
        pass

    onkeyrelease = onkey



    def onkeypress(self, fun, key=None):
        '''
        パラメタ:
        :param fun : a function with no arguments or None
        :param key : a string: key (e.g. "a") or key-symbol (e.g. "space")
        Bind fun to key-press event of key if key is given,
        or to any key-press-event if no key is given. Remark:
        in order to be able to register key-events,
        TurtleScreen must have focus. (See method listen().)

        >>> def f():
        ...     fd(50)
        ...
        >>> screen.onkey(f, "Up")
        >>> screen.listen()
        '''
        pass



    def onscreenclick(self, fun, btn=1, add=None):
        '''
        パラメタ:
        :param fun : a function with two arguments which will be called with the coordinates of
                     the clicked point on the canvas
        :param num : number of the mouse-button, defaults to 1 (left mouse button)
        :param add : True or False -- if True, a new binding will be added, otherwise it will
                     replace a former binding
        fun をタートルのマウスクリック(mouse-click)イベントに束縛します。 fun が None ならば、
        既存の束縛が取り除かれます。

        Example for a screen という名の TurtleScreen インスタンスと turtle という名前の Turtle インスタンスの例:

        >>> screen.onclick(turtle.goto) # Subsequently clicking into the TurtleScreen will
        >>>                             # make the turtle move to the clicked point.
        >>> screen.onclick(None)        # remove event binding again
        注釈 この TurtleScreen メソッドはグローバル関数としては onscreenclick という名前でだけ使えます。
        グローバル関数 onclick は Turtle メソッドの onclick から派生した別ものです。
        '''
        pass



    def ontimer(self, fun, t=0):
        '''
        パラメタ:
        :param fun : a function with no arguments
        :param t : a number >= 0
        t ミリ秒後に fun を呼び出すタイマーを仕掛けます。

        >>> running = True
        >>> def f():
        ...     if running:
        ...         fd(50)
        ...         lt(60)
        ...         screen.ontimer(f, 250)
        >>> f()   ### makes the turtle march around
        >>> running = False
        '''
        pass



    def mainloop(self):
        '''
        Starts event loop - calling Tkinter’s mainloop function. Must be the last statement in
        a turtle graphics program. Must not be used if a script is run from within IDLE
        in -n mode (No subprocess) - for interactive use of turtle graphics.

        >>> screen.mainloop()
        24.1.4.4. Input methods
        '''
        pass

    done = mainloop



    def textinput(self, title, prompt):
        '''
        パラメタ:
        :param title : string
        :param prompt : string
        Pop up a dialog window for input of a string. Parameter title is the title of
        the dialog window, propmt is a text mostly describing what information to input.
        Return the string input. If the dialog is canceled, return None.

        >>> screen.textinput("NIM", "Name of first player:")
        '''
        pass



    def numinput(self, title, prompt, default=None, minval=None, maxval=None):
        '''
        パラメタ:
        :param title : string
        :param prompt : string
        :param default : number (optional)
        :param minval : number (optional)
        :param maxval : number (optional)
        Pop up a dialog window for input of a number. title is the title of the dialog window,
        prompt is a text mostly describing what numerical information to input.
        default: default value,
        minval: minimum value for imput,
        maxval: maximum value for input
        The number input must be in the range minval .. maxval if these are given.
        If not, a hint is issued and the dialog remains open for correction.
        Return the number input. If the dialog is canceled, return None.

        >>> screen.numinput("Poker", "Your stakes:", 1000, minval=10, maxval=10000)
        24.1.4.5. 設定と特殊なメソッド
        '''
        pass



    def mode(self, mode=None):
        '''
        :param mode : one of the strings "standard", "logo" or "world"
        タートルのモード("standard", "logo", "world" のいずれか)を設定してリセットします。
        モードが渡されなければ現在のモードが返されます。

        モード "standard" は古い turtle 互換です。モード "logo" は Logo タートルグラフィックスと
        ほぼ互換です。モード "world" はユーザーの定義した「世界座標(world coordinates)」を使います。
        重要なお知らせ: このモードでは x/y 比が 1 でないと角度が歪むかもしれません。

        モード
        タートルの向きの初期値
        正の角度
        "standard"
        右 (東) 向き
        反時計回り
        "logo"
        上 (北) 向き
        時計回り
        >>> mode("logo")   # resets turtle heading to north
        >>> mode()
        'logo'
        '''
        pass



    def colormode(self, cmode=None):
        '''
        :param cmode : one of the values 1.0 or 255
        色モード(colormode)を返すか、または 1.0 か 255 のどちらかの値に設定します。
        設定した後は、色トリプルの r, g, b 値は 0 から cmode の範囲になければなりません。

        >>> screen.colormode(1)
        >>> turtle.pencolor(240, 160, 80)
        Traceback (most recent call last):
             ...
        TurtleGraphicsError: bad color sequence: (240, 160, 80)
        >>> screen.colormode()
        1.0
        >>> screen.colormode(255)
        >>> screen.colormode()
        255
        >>> turtle.pencolor(240,160,80)
        '''
        pass



    def getcanvas(self):
        '''
        この TurtleScreen の Canvas を返します。 Tkinter の Canvas を使って何をするか
        知っている人には有用です。

        >>> cv = screen.getcanvas()
        >>> cv
        <turtle.ScrolledCanvas object at ...>
        '''
        pass



    def getshapes(self):
        '''
        現在使うことのできる全てのタートルの形のリストを返します。

        >>> screen.getshapes(),
        ['arrow', 'blank', 'circle', ..., 'turtle']
        '''
        pass



    def register_shape(self, name, shape=None):
        '''
        この関数を呼び出す三つの異なる方法があります:

        name が gif ファイルの名前で shape が None: 対応する画像の形を取り込みます。

        >>> screen.register_shape("turtle.gif")
        注釈 画像の形はタートルが向きを変えても 回転しません ので、
        タートルがどちらを向いているか見ても判りません!
        name が任意の文字列で shape が座標ペアのタプル: 対応する多角形を取り込みます。

        >>> screen.register_shape("triangle", ((5,-3), (0,5), (-5,-3)))
        name が任意の文字列で shape が (合成形の) Shape オブジェクト: 対応する合成形を取り込みます。

        タートルの形を TurtleScreen の形リスト(shapelist)に加えます。このように登録された形だけが
        shape(shapename) コマンドに使えます。

        '''
        pass

    addshape = register_shape


    def turtles(self):
        '''
        スクリーン上のタートルのリストを返します。

        >>> for turtle in screen.turtles():
        ...     turtle.color("red")
        '''
        pass



    def window_height(self):
        '''
        タートルウィンドウの高さを返します。

        >>> screen.window_height()
        480
        '''
        pass



    def window_width(self):
        '''
        タートルウィンドウの幅を返します。

        >>> screen.window_width()
        640
        24.1.4.6. Screen 独自のメソッド、TurtleScreen から継承したもの以外
        '''
        pass



    def bye(self):
        '''
        タートルグラフィックス(turtlegraphics)のウィンドウを閉じます。

        '''
        pass



    def exitonclick(self):
        '''
        スクリーン上のマウスクリックに bye() メソッドを束縛します。

        設定辞書中の "using_IDLE" の値が False (デフォルトです) の場合、
        さらにメインループ(mainloop)に入ります。注意: もし IDLE が
        -n スイッチ(サブプロセスなし)付きで使われているときは、
        この値は turtle.cfg の中で True とされているべきです。
        この場合、IDLE のメインループもクライアントスクリプトから見て
        アクティブです。

        '''
        pass



    def setup(self, width=0.5, height=0.75, startx=None, starty=None):
        '''
        メインウィンドウのサイズとポジションを設定します。引数のデフォルト値は設定辞書に収められており、
        turtle.cfg ファイルを通じて変更できます。

        パラメタ:
        :param width : if an integer, a size in pixels, if a float, a fraction of the screen;
                       default is 50% of screen
        :param height : if an integer, the height in pixels, if a float, a fraction of the screen;
                        default is 75% of screen
        :param startx : if positive, starting position in pixels from the left edge of the screen,
                        if negative from the right edge, if None, center window horizontally
        :param startx : if positive, starting position in pixels from the top edge of the screen,
                        if negative from the bottom edge, if None, center window vertically
        >>> screen.setup (width=200, height=200, startx=0, starty=0)
        >>>              # sets window to 200x200 pixels, in upper left of screen
        >>> screen.setup(width=.75, height=0.5, startx=None, starty=None)
        >>>              # sets window to 75% of screen by 50% of screen and centers
        '''
        pass



    def title(self, titlestring):
        '''
        :param titlestring : a string that is shown in the titlebar of the turtle graphics window
        ウインドウのタイトルを titlestring に設定します。

        >>> screen.title("Welcome to the turtle zoo!")
        '''
        pass

    '''
        24.1.5. Public classes
        class turtle.RawTurtle(canvas)
        class turtle.RawPen(canvas)
        :param canvas : a tkinter.Canvas, a ScrolledCanvas or a TurtleScreen
        タートルを作ります。タートルには上の「Turtle/RawTurtle のメソッド」で説明した全てのメソッドがあります。

        class turtle.Turtle
        RawTurtle のサブクラスで同じインターフェイスを持ちますが、最初に必要になったとき自動的に作られる
        Screen オブジェクトに描画します。

        class turtle.TurtleScreen(cv)
        :param cv : a tkinter.Canvas
        上で説明した setbg() のようなスクリーン向けのメソッドを提供します。

        class turtle.Screen
        TurtleScreen のサブクラスで 4つのメソッドが加わっています 。

        class turtle.ScrolledCanvas(master)
        :param master : some Tkinter widget to contain the ScrolledCanvas,
        i.e. a Tkinter-canvas with scrollbars added
        タートルたちが遊び回る場所として自動的に ScrolledCanvas を提供する
        Screen クラスによって使われます。

        class turtle.Shape(type_, data)
        :param type_ : one of the strings "polygon", "image", "compound"
        形をモデル化するデータ構造。ペア (type_, data) は以下の仕様に従わなければなりません:

        type_	data
        "polygon"
        多角形タプル、すなわち座標ペアのタプル
        "image"
        画像 (この形式は内部的にのみ使用されます!)
        "compound"
        None (合成形は addcomponent() メソッドを使って作らなければなりません)
        addcomponent(poly, fill, outline=None)
        パラメタ:
        :param poly : a polygon, i.e. a tuple of pairs of numbers
        :param fill : a color the poly will be filled with
        :param outline : a color for the poly’s outline (if given)
        例:

        >>> poly = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s = Shape("compound")
        >>> s.addcomponent(poly, "red", "blue")
        >>> # ... add more components and then use register_shape()
        Compound shapes を参照。

        class turtle.Vec2D(x, y)
        2次元ベクトルのクラスで、タートルグラフィックスを実装するための補助クラス。
        タートルグラフィックスを使ったプログラムでも有用でしょう。
        タプルから派生しているので、ベクターはタプルです!

        以下の演算が使えます (a, b はベクトル、 k は数):

        a + b ベクトル和

        a - b ベクトル差

        a * b 内積

        k * a および a * k スカラー倍

        abs(a) a の絶対値

        a.rotate(angle) 回転

        24.1.6. ヘルプと設定
        24.1.6.1. ヘルプの使い方
        Screen と Turtle クラスのパブリックメソッドはドキュメント文字列で網羅的に文書化
        されていますので、Python のヘルプ機能を通じてオンラインヘルプとして利用できます:

        IDLE を使っているときは、打ち込んだ関数/メソッド呼び出しのシグニチャとドキュメント文字列
        の一行目がツールチップとして表示されます。

        help() をメソッドや関数に対して呼び出すとドキュメント文字列が表示されます:

        >>> help(Screen.bgcolor)
        Help on method bgcolor in module turtle:

        bgcolor(self, *args) unbound turtle.Screen method
            Set or return backgroundcolor of the TurtleScreen.

            Arguments (if given): a color string or three numbers
            in the range 0..colormode or a 3-tuple of such numbers.


              >>> screen.bgcolor("orange")
              >>> screen.bgcolor()
              "orange"
              >>> screen.bgcolor(0.5,0,0.5)
              >>> screen.bgcolor()
              "#800080"

        >>> help(Turtle.penup)
        Help on method penup in module turtle:

        penup(self) unbound turtle.Turtle method
            Pull the pen up -- no drawing when moving.

            Aliases: penup | pu | up

            No argument

            >>> turtle.penup()
        メソッドに由来する関数のドキュメント文字列は変更された形をとります:

        >>> help(bgcolor)
        Help on function bgcolor in module turtle:

        bgcolor(*args)
            Set or return backgroundcolor of the TurtleScreen.

            Arguments (if given): a color string or three numbers
            in the range 0..colormode or a 3-tuple of such numbers.

            Example::

              >>> bgcolor("orange")
              >>> bgcolor()
              "orange"
              >>> bgcolor(0.5,0,0.5)
              >>> bgcolor()
              "#800080"

        >>> help(penup)
        Help on function penup in module turtle:

        penup()
            Pull the pen up -- no drawing when moving.

            Aliases: penup | pu | up

            No argument

            Example:
            >>> penup()
        これらの変更されたドキュメント文字列はインポート時にメソッドから導出される関数定義と
        一緒に自動的に作られます。

        '''

    def write_docstringdict(self, filename="myturtle_docstringdict"):
        '''
        :param filename : a string, used as filename
        ドキュメント文字列辞書(docstring-dictionary)を作って与えられたファイル名の
        Python スクリプトに書き込みます。この関数はわざわざ呼び出さなければなりません
        (タートルグラフィックスのクラスから使われることはありません)。
         ドキュメント文字列辞書は filename.py という Python スクリプトに書き込まれます。
         ドキュメント文字列の異なった言語への翻訳に対するテンプレートとして使われる
         ことを意図したものです。

        もしあなたが(またはあなたの生徒さんが) turtle を自国語のオンラインヘルプ付きで
        使いたいならば、ドキュメント文字列を翻訳してできあがったファイルをたとえば
        turtle_docstringdict_german.py という名前で保存しなければなりません。

        さらに turtle.cfg ファイルで適切な設定をしておけば、このファイルがインポート時に
        読み込まれて元の英語のドキュメント文字列を置き換えます。

        この文書を書いている時点ではドイツ語とイタリア語のドキュメント文字列辞書が存在します。
         (glingl@aon.at にリクエストして下さい。)
        '''
        pass

    '''
        24.1.6.3. Screen および Turtle の設定方法
        初期デフォルト設定では古い turtle の見た目と振る舞いを真似るようにして、
        互換性を最大限に保つようにしています。

        このモジュールの特性を反映した、あるいは個々人の必要性 (たとえばクラスルームでの使用)に
        合致した、異なった設定を使いたい場合、設定ファイル turtle.cfg を用意してインポート時に
        読み込ませその設定に従わせることができます。

        初期設定は以下の turtle.cfg に対応します:

        width = 0.5
        height = 0.75
        leftright = None
        topbottom = None
        canvwidth = 400
        canvheight = 300
        mode = standard
        colormode = 1.0
        delay = 10
        undobuffersize = 1000
        shape = classic
        pencolor = black
        fillcolor = black
        resizemode = noresize
        visible = True
        language = english
        exampleturtle = turtle
        examplescreen = screen
        title = Python Turtle Graphics
        using_IDLE = False
        いくつかピックアップしたエントリーの短い説明:

        最初の4行は Screen.setup() メソッドの引数に当たります。

        5行目6行目は Screen.screensize() メソッドの引数に当たります。

        shape は最初から用意されている形ならどれでも使えます(arrow, turtle など)。
        詳しくは help(shape) をお試し下さい。

        塗りつぶしの色(fillcolor)を使いたくない(つまりタートルを透明にしたい)場合、
        fillcolor = "" と書かなければなりません (しかし全ての空でない文字列は
                                                 cfg ファイル中で引用符を付けてはいけません)。

        タートルにその状態を反映させるためには resizemode = auto とします。

        たとえば language = italian とするとドキュメント文字列辞書(docstringdict)
        として turtle_docstringdict_italian.py がインポート時に読み込まれます
        (もしそれがインポートパス、たとえば turtle と同じディレクトリにあれば)。

        exampleturtle および examplescreen はこれらのオブジェクトのドキュメント文字列内での
        呼び名を決めます。メソッドのドキュメント文字列から関数のドキュメント文字列に変換する際に、
        これらの名前は取り除かれます。

        using_IDLE: IDLE とその -n スイッチ(サブプロセスなし)を常用するならば、
        この値を True に設定して下さい。これにより exitonclick() がメインループ(mainloop)に入る
        のを阻止します。

        '''

class MyTurtle(Turtle):
    '''
    最初，オリジナルの Turtle と区別するために MyTurtle という名前で作り始めたが，
    やはりMyとか付けとくのはあまりよくないので，改名した．
    旧バージョンとの互換を保つための子クラス
    '''
    def __init__(self):
        super().__init__()
        print('Class "MyTurtle" is obsolete. Use "Turtle".')


# -----------------------------------------------------

class TurtlePicture:

    def __init__(self, start_pt=None):

        self.__pen = {}
        if start_pt is None:
            self.__points = []
        else:
            self.__points = [start_pt]

    def get_svg(self):
        pass

    def set_pen(self, pen):
        self.__pen = pen

    def push_point(self, pt):
        self.__points += [pt]

    def get_pen(self):
        return self.__pen

    def get_points(self):
        return self.__points


class Polyline(TurtlePicture):

    def __init__(self, start_pt=None):
        super().__init__(start_pt)

    # TODO: このあたりは，本来TurtlePictureに持たせる機能ではなく 
    # SvgElementの機能でTurtlePictureを受け取って処理するべきだろう
    def get_svg(self, unit_width=0.5, unit_length=1):
        pen = self.get_pen()
        attrs = {
                'stroke-width': pen['pensize'] * unit_width,
                'fill' : 'none',
                #TODO 'red'とか'blue'でないRGB指定をサポートしたい
                'stroke' : pen['pencolor']
                }
        points_vec2d = self.get_points()

        ul = unit_length
        # y座標を反転
        points = [(pt[0]*ul, -pt[1]*ul) for pt in points_vec2d]
        svg_polyline = svg.SvgPolyline(points, attrs)

        return svg_polyline

    def get_tikz_form(self, unit_width=0.5, unit_length=0.03, indent_depth=2):
        '''
        \\draw [_options] (x0, y0) -- (x1, y1) -- ... -- (xn, yn);
        の形の文字列を返す．
        '''
        _pen = self.get_pen()
        _stroke_width = _pen['pensize'] * unit_width
        _stroke_color = _pen['pencolor']
        _points = self.get_points()

        indent_space = ' ' * indent_depth

        _options = 'line width={}pt'.format(_stroke_width)
        if _stroke_color != 'black':
            #TODO 'red'とか'blue'でないRGB指定をサポートしたい
            _options += ', color={}'.format(_stroke_color)

        tikz = indent_space + r'\draw [{}]'.format(_options)

        tikz += '\n' + indent_space * 2 + '   '
        for cnt, pt in enumerate(_points):
            tikz += ' ({x:>.4f}, {y:>.4f})'.format(x=pt[0]*unit_length,
                                         y=pt[1]*unit_length)
            if cnt < len(_points)-1:
                tikz += '\n' + indent_space * 2 +' --'
            else:
                tikz += ';'

        return tikz


class Path(TurtlePicture):
    
    def __init__(self, start_pt=None, filling=False):
        super().__init__(start_pt)
        
        self.d_list = []
        if start_pt:
            self.append_pt(start_pt)
        self.filling = filling
    
    def was_moved(self):
        '''
        2点以上が記録されているかどうかを返す．
        （1点の場合は，start_ptのみで，移動してない）
        '''
        return len(self.d_list) > 1
    
    def append_pt(self, pt):
        self.d_list.append(DM(pt[0], pt[1]))

    def append_line_to(self, pt):
        self.d_list.append(DL(pt[0], pt[1]))
    
    def append_arc(self, rx, ry, start, f1, f2, x, y):
        self.d_list.append(DA(rx, ry, start, f1, f2, x, y))
    
    def append_d(self, d_attr_obj):
        self.d_list.append(d_attr_obj)

    def close_path(self):
        '''
        pathを閉路にする（SVGのpathの末尾に'Z'を追加する．）
        基本的にはend_fill()が実行されたときのみを想定．
        '''
        self.d_list.append(DAttrObj('Z'))
        
    def get_svg(self, unit_width=0.5, unit_length=1):
        pen = self.get_pen()
        if self.filling:
            fillcolor = pen['fillcolor']
            pen['pencolor'] = 'none'
        else:
            fillcolor = 'none'
        attrs = {
                'stroke-width': pen['pensize'] * unit_width,
                'fill' : fillcolor,
                'stroke' : pen['pencolor']
                }

        ul = unit_length
        
        d_taples = []
        for d in self.d_list:
            d_taples.append(d.get_d_tuple(ul, -1))
        svg_path = svg.SvgPath(d_taples, attrs)

        return svg_path

class DAttrObj():
    '''
    svg path の d属性の中身
      DM: "M x y "
      DA: "A rx ry start f1 f2 x2 y2 "
      を想定
    '''
    def __init__(self, name, items=[]):
        self.name = name
        self.items = items
    
    def get_d_tuple(self, ul=1, y_sgn=-1):
        '''
        ("M", real_x, real_y)
        ("A", real_rx, real_rx, start, f1, f2, real_x, real_y)
        のようなものを返す
        '''
        return tuple([self.name] + self.items)

class DM(DAttrObj):
    '''
    M x y 
    '''
    def __init__(self, x, y):
        super().__init__('M')
        self.x = x
        self.y = y
    
    def get_d_tuple(self, ul=1, y_sgn=-1):
        return ('M', self.x*ul, self.y*ul*y_sgn)

class DL(DAttrObj):
    '''
    L x y 
    '''
    def __init__(self, x, y):
        super().__init__('L')
        self.x = x
        self.y = y
    
    def get_d_tuple(self, ul=1, y_sgn=-1):
        return ('L', self.x*ul, self.y*ul*y_sgn)
        
class DA(DAttrObj):    
    '''
    A  rx ry start f1 f2 x2 y2
    '''
    def __init__(self, rx, ry, start, f1, f2, x, y):
        super().__init__('A')
        self.rx = rx
        self.ry = ry
        self.start = start
        self.f1 = f1
        self.f2 = f2
        self.x = x
        self.y = y
    
    def get_d_tuple(self, ul=1, y_sgn=-1):
        return ('A', self.rx*ul, self.ry*ul, 
                     self.start, self.f1, self.f2,
                     self.x*ul, self.y*ul*y_sgn)

class Circles:
    '''
    circle 1個1個をCircleオブジェクトみたいに作ると，
    dotを大量に描画した場合などにおそらく重すぎる．
    (cx, cy, radius, color)のリストを保持させて，
    get_svgで一気に出力させる．
    '''
    def __init__(self):
        self.circles = []
    
    def append_circle(self, circle_tuple):
        self.circles.append(circle_tuple)
