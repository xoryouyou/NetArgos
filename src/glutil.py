"""
    A simple collection of drawing and projection utilities in pyglet
"""

from pyglet.gl import glLineWidth, glEnable, glColor4f,glColor3f, glBegin,\
                      glVertex3f, glEnd, GL_LINE_SMOOTH, GL_TEXTURE_2D,\
                      GL_LINE_STRIP, gluNewQuadric, glPushMatrix, glPopMatrix,\
                      glGetDoublev, GL_MODELVIEW_MATRIX, GL_PROJECTION_MATRIX,\
                      gluProject, gluUnProject, GL_VIEWPORT, c_double,\
                      c_int, glGetIntegerv, glDisable, glTranslatef, gluDisk,\
                      GL_QUADS, GL_LINES

from pyglet.graphics import draw


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
    glColor4f(color[0], color[1], color[2], alpha)

    glLineWidth(width)
    if aa:
        glEnable(GL_LINE_SMOOTH)

    draw(2, GL_LINES, ('v2f', (a[0], a[1], b[0], b[1])))


def circle(pos, radius, color=(1.0, 1.0, 1.0), alpha=1.0, segments=6):
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
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)


def rect(a, b, color=(1.0,1.0,1.0), alpha=1.0):
    """
    Draws a rectangle in the plane spanned by a,b with GL_QUADS

    :param a: Point a
    :type a: 2-float tuple

    :param b: Point b
    :type b: 2-float tuple

    :param color: the color in [0..1] range
    :type color: 3-float tuple

    :param aa: Anti aliasing Flag

    :param alpha: the alpha value in [0..1] range

    """

    glDisable(GL_TEXTURE_2D)

    glBegin(GL_QUADS)
    glVertex3f(a[0], a[1], 0)
    glVertex3f(b[0], a[1], 0)
    glVertex3f(b[0], b[1], 0)
    glVertex3f(a[0], b[1], 0)

    glEnd()
    glEnable(GL_TEXTURE_2D)
    glColor4f(color+(alpha,))


def screen_to_model(c):
    """
    Returns the 3D coordinate of given screen coordinate

    :param c: The screen coordinates for example
    :type c: 3-tuple of float  (x,y,0)

    :rtype: 3-tuple float (x,y,z)

    """
    m = (c_double*16)()
    glGetDoublev(GL_MODELVIEW_MATRIX, m)

    p = (c_double*16)()
    glGetDoublev(GL_PROJECTION_MATRIX, p)

    v = (c_int*4)()
    glGetIntegerv(GL_VIEWPORT, v)

    x, y, z = c_double(), c_double(), c_double()

    y.value = v[3] - y.value
    gluUnProject(c[0], c[1], c[2], m, p, v, x, y, z)

    return x, y, z


def model_to_screen(c):
    """
    Returns the screen point of given 3D coordinate

    :param c: The 3D coordinates
    :type c: 3-tuple of float (x,y,z)

    :rtype: 3-tuple float (x,y,z)

    """
    m = (c_double*16)()
    glGetDoublev(GL_MODELVIEW_MATRIX, m)

    p = (c_double*16)()
    glGetDoublev(GL_PROJECTION_MATRIX, p)

    v = (c_int*4)()
    glGetIntegerv(GL_VIEWPORT, v)

    x, y, z = c_double(), c_double(), c_double()
    gluProject(c[0], c[1], c[2], m, p, v, x, y, z)

    return x, y, z

