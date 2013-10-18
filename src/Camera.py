from pyglet.gl import *
from glutil import screen_to_model

class Camera(object):
    """
     A Camera Class for scroll,zoom and projection helper functions
    """

    def __init__(self, win, x=0.0, y=0.0, zoom=1.0):
        """
        :params win: The main window
        :type win: pyglet.window

        :params x: Horizontal camera offset
        :type x: float

        :params y: Vertical camera offset 
        :type y: float

        :params zoom: View scaling factor
        :type zoom: float

        .. note::
            zoom needs to be > 1.0
            

        """
        self.win = win
        self.x = x
        self.y = y
        self.zoom = zoom
        self.zoomTo = (c_double(), c_double())

    def worldProjection(self):
        """
        Uses gluOrtho2D to center the screen to :py:data:`Camera.x` , :py:data:`Camera.y` and then scales it depending on :py:data:`Camera.zoom`
        """
    
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        centerX, centerY = self.win.width//2, self.win.height//2

        z = 1.0/self.zoom
        l = self.zoomTo[0].value - centerX * z
        r = self.zoomTo[0].value + centerX * z
        t = self.zoomTo[1].value + centerY * z
        b = self.zoomTo[1].value - centerY * z
        glOrtho(l, r, t, b, 1.0, -1.0)

        glTranslatef(-self.x, -self.y, 0)


    def hudProjection(self):
        """
        Uses gluOrtho2D to change into HUD-Mode 

        ======  =============
        Bound   Value
        ======  =============
        left    0
        right   window.width
        bottom  0
        top     window.height
        ======  =============

        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D( 0, self.win.width, 0, self.win.height)
