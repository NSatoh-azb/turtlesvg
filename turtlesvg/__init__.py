# -*- coding: utf-8 -*-
'''
  タートルグラフィックスの出力をSVGで保存するためのパッケージ
  
  spyderなど、IPython環境では、マジックコマンド
      %gui tk
  を実行してから利用する。（そうしないと動作が不安定）
    
  -+-+- 使い方 -+-+-
    
      import trutlesvg as ttl
      t = ttl.MyTurtle()
      
    として、MyTurtleオブジェクト t を生成する。
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
                #!-- 重要 --!#
      t.penup() # 保存前に1度ペンアップの実行が必要
      t.save_svg("filename.svg")
        
    などとすると、"filename.svg"にSVGファイルが保存される。  
'''

from .turtlesvg import MyTurtle

__all__ = ['MyTurtle']
