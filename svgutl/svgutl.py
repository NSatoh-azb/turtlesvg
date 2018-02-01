"""
@author: NSatoh
Azabu high school, department of mathematics

SVG utilities for turtlesvg package.
"""
class Svg:

    def __init__(self, w=1000, h=1000, x0=-500, y0=-500, vb_w=1000, vb_h=1000):
        self.head = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
        self.head += '<svg xmlns="http://www.w3.org/2000/svg"' + '\n'
        self.head += '     xmlns:xlink="http://www.w3.org/1999/xlink"' + '\n'
        self.head += f'     width="{w}" height="{h}" viewBox="{x0} {y0} {vb_w} {vb_h}">' + '\n'
        self.body = ''
        self.foot = '</svg>'

    def append_element(self, svg_element):
        self.body += svg_element.get_svg() + '\n'

    def get_svg(self):
        svg = self.head
        svg += self.body
        svg += self.foot
        return svg


class SvgElement:

    def __init__(self, name, attributes):
        self.name = name
        self.head_begin = f'<{name}'
        self.head_body = ''
        self.head_end = '/>'
        self.data = ''
        self.foot = ''
        for attr_name in attributes:
            self.head_body += f' {attr_name}='
            self.head_body += f'"{attributes[attr_name]}"'

    def append_attribute(self, attr_name, attribute):
        self.head_body += f' {attr_name}='
        self.head_body += f'"{attribute}"'
        
    def append_data(self, data):
        self.data += data
        # data が存在する場合は終了タグを変更
        self.head_end = '>'
        self.foot = f'</{self.name}>'

    def append_svg_data(self, svg_element):
        self.data += svg_element.get_svg()
        # data が存在する場合は終了タグを変更
        self.head_end = '>'
        self.foot = f'</{self.name}>'

    def get_svg(self):
        svg = self.head_begin
        svg += self.head_body
        svg += self.head_end
        svg += self.data
        svg += self.foot
        return svg


class SvgPolyline(SvgElement):

    def __init__(self, points=None, attributes=None):
        super().__init__(name='polyline', attributes=attributes)
        self.points = points

    def append_point(self, pt):
        self.points += [pt]  
        
    def gen_points_str(self):
        pts = 'points="'
        for pt in self.points:
            pts += f'{pt[0]} {pt[1]} '
        pts += '"'
        return pts

    def get_svg(self):
        svg = self.head_begin
        svg += self.head_body
        svg += ' ' + self.gen_points_str()
        svg += self.head_end
        svg += self.data
        svg += self.foot
        return svg

