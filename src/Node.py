

from glutil import circle, line
from pyglet import text


class Node(object):
    """
     A Class to represent a network Node.
    """

    def __init__(self, data, position, color=(1.0, 1.0, 1.0), size=8):
        """
        :param data: Contains all needed information from GeoIP and psutil(netstat).
        :type data: dict
        
        :param position: absolute X/Y pixel-position on the worldmap
        :type position: 2-tuple
        
        :ivar color: default (1.0, 1.0, 1.0)
        :ivar size: default 8
        """
        self.data = data
        for key in [key for key in self.data.keys() if self.data[key] == ""]:
            self.data[key] = None
        self.position = position
        self.onScreen = (0.0, 0.0)
        self.color = color
        self.size = size
        self.connections = []
        self.hover = False
        self.expanded = False

    #FIXME make string functions static

    def labelString(self):
        """
        :returns: A string containing the geolocation information to draw the Label above the Node
        """
        return (str(self.data["city"]).decode('latin-1')+","+\
                str(self.data["region_name"]).decode('latin-1')+","+\
                str(self.data["country_code"]).decode('latin-1') )

    def toString(self):
        """
        :returns: A string containing extended information for :py:meth:`NetArgos.NetArgos.drawNetstat`
        """
        return(str(self.data["local"]).rjust(21)+"  ->  "+\
                str(self.data["remote"]).rjust(21)+" "+\
                str(self.data["name"]).rjust(10)+\
                str(self.data["status"]).rjust(10)+\
                str(self.data["city"]).decode('latin-1').rjust(10)+"/"+\
                 str(self.data["country_code"]).decode('latin-1').rjust(3))

    def getHoverInfo(self):
        """
        :returns: string containing extended information for drawing the label hover in :py:meth:`NetArgos.NetArgos.on_draw`
        """
        info = "IP: %-21s\n"+\
                "Type: %-20s\n"+\
                "Country: %-20s\n"+\
                "Region: %-20s\n"+\
                "City: %-20s\n"+\
                "Lat: %-20s\n"+\
                "Long: %-20s"
                
                
        info = info%(str(self.data["remote"]),
                     str(self.data["status"]),
                     str(self.data["country_name"]),
                     str(self.data["region_name"]).decode('latin-1'),
                     str(self.data["city"]).decode('latin-1'),
                     str(self.data["latitude"]),
                     str(self.data["longitude"]) )
        return info

    def draw(self):

        for c in self.connections:
            line(self.onScreen, c.onScreen, (0.5, 0.5, 0.5))
        if self.hover:
            circle(self.onScreen, self.size, self.color)
            label = text.Label(self.getHoverInfo(), font_name="Droid Sans Mono", font_size=8,x=self.onScreen[0]+10, y=self.onScreen[1]-5,multiline=True,width=400)
            label.draw()
        else:
            circle(self.onScreen, self.size, (0.5, 0.5, 0.5))
        label = text.Label(self.labelString(), font_name="Droid Sans Mono", font_size=10,x=self.onScreen[0], y=self.onScreen[1]+10)
        label.draw()





