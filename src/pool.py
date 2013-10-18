import pyglet

from multiprocessing.pool import ThreadPool


from pyglet.gl import glLineWidth, glEnable, glColor4f,glColor3f, glBegin,glVertex3f,glEnd,\
    GL_LINE_SMOOTH,GL_TEXTURE_2D,GL_LINE_STRIP,gluNewQuadric,glPushMatrix,glPopMatrix,\
    glGetDoublev,GL_MODELVIEW_MATRIX,GL_PROJECTION_MATRIX,gluProject,gluUnProject,GL_VIEWPORT,\
    c_double,c_int,glGetIntegerv,glDisable,glTranslatef,gluDisk,GL_QUADS,GL_LINES

from pyglet.graphics import draw

from math import pi, cos, sin
def line(a, b, color=(1.0,1.0,1.0), width=1, aa=False, alpha=1.0):
    """
    Draws a line from point *a* to point *b* using GL_LINE_STRIP optionaly with GL_LINE_SMOOTH when *aa=True*

    :param a: Point a
    :type a: 2-float tuple

    :param b: Point b
    :type b: 2-float tuple

    :param color: the color in [0..1] range
    :type color: 3-float tuple

    :param width: The with for glLineWidth()

    :param aa: Anti aliasing Flag

    :param alpha: the alpha value in [0..1] range

    """

    glLineWidth(width)
    if aa:
        glEnable(GL_LINE_SMOOTH)

    draw(2,GL_LINES,('v2f',(a[0],a[1],b[0],b[1]) ) )

def circle(pos, radius, color=(1.0,1.0,1.0), alpha=1.0,segments=6):
    """
    Draws a circle with gluDisk 
    
    :param pos: center of the circle
    :type pos: 2-float tuple

    :param radius: radius of the circle
    :type radius: float

    :param color: the color in [0..1] range
    :type color: 3-float tuple

    :param alpha: the alpha value in [0..1] range

    :param segments: number of segments
    :type segments: int

    """

    glDisable(GL_TEXTURE_2D)

    c = gluNewQuadric()
    glColor4f(color[0], color[1], color[2], alpha)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], 0)
    gluDisk(c, 0, radius, segments, 1)
    glPopMatrix()
    glColor4f(1.0,1.0,1.0,1.0)
    glEnable(GL_TEXTURE_2D)



class Foo(pyglet.window.Window):
    def __init__(self):
        super(Foo,self).__init__(400,400)
        l = pyglet.text.Label('FOOBAR',font_name="Courier Sans",font_size=20,x=self.width//2,y=self.height//2,multiline=True,width=200)


        pool = ThreadPool(processes=1)
        self.r = pool.apply_async(foo)


        @self.event
        def on_key_press(s,m):
            if s == pyglet.window.key.C:
                print("EXTERNAL")
                l.text = self.r.get()


        @self.event
        def on_draw():
            self.clear()
            
            l.draw()
            count = 10
            offset =(2*pi)/ 10.0
            for i in range(count):
                line((200,200),(200+cos(offset*i)*100,200+sin(offset*i)*100))

        pyglet.app.run()


def foo():
    return '123.456.789'


if __name__ == '__main__':
    f = Foo()
