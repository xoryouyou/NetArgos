from pyglet import window, app, clock, text
from pyglet.gl import *
from pyglet.window import key, mouse
from pyglet.graphics import vertex_list, Batch
from multiprocessing.pool import ThreadPool
import getopt
import sys
from math import cos, sin, pi

from pygeoip import GeoIP, MEMORY_CACHE
import cPickle as pickle

from glutil import line, circle, screen_to_model, model_to_screen
from netutil import getExternalIp, getConnections
from Camera import Camera
from Mercator import Mercator
from Node import Node


class NetArgos(window.Window):
    """
     The main class which inherits the pyglet.window.Window class.
    """
    def __init__(self, xres=1280, yres=720):

        if sys.version_info < ( 2,7):
            print("Please use python 2.7.x , python 3.x preferred")
            self.usage()
            sys.exit(1)
        elif sys.version_info <  (3, 2):
            print("[-] Warning NetArgos is made under python 3.2, please keep in mind when bugs occur.")


        self.expandMode = False
        self.hovering = False
        self.foundLocalIp = False
        self.localIp = None
        self.nodes = []
        self.localNode = None
        self.drawNetstatOverlay = False
        self.mousePos= (0, 0)
        self.version = 0.1
        self.geodbfile = '../data/GeoLiteCity.dat'
        self.fontname = "Courier"
        self.fontsize = 8
       
        self.version = 0.1
        self.debug = False
        self.localNodeData = {}
        self.localNodePosition = None
        
        try:
            opts, args = getopt.getopt( sys.argv[1:],
                                        'i:vd',
                                        ['ip=',
                                        'debug',
                                        'version',
                                        'geodb=',
                                        'resolution='])
                                        
        except getopt.GetoptError as e:
            print(e)
            self.usage()
            
        for o,a in opts:
            if o in ('-i','--ip'):
                if '=' in a:
                    self.localIp = a.split('=')[1]
                else:
                    self.localIp = a
                self.foundLocalIp = True

            elif o in ('-v','--version'):
                print("%s: Version %s" %(sys.argv[0],self.version))
                sys.exit(0)
            elif o in ('-d','--debug'):
                self.debug = True
            elif o == '--geodb':
                self.geodbfile = a
                
            elif o == '--resolution':
                if 'x' in a:
                    xres, yres = a.split('x')[:2]
                    xres=int(xres)
                    yres=int(yres)
                else:
                    self.usage()
            else:
                self.usage()
                sys.exit(1)


        super(NetArgos, self).__init__(xres, yres)
        self.batch = Batch()
        self.labelBatch = Batch()
      
        
        try:
            self.geoIP = GeoIP(self.geodbfile,MEMORY_CACHE)
        except Exception as e:
            print('[-] Failed loading %s", %s' %(self.geodbfile, e))
            exit(1)


        self.pool = ThreadPool(processes=1)
        self.fps = clock.ClockDisplay()


        self.loadPaths('../data/borders-50-batched.bin',(0,100,0))
        self.loadPaths('../data/coast-50-batched.bin',(0,255,0))

        self.camera = Camera(self, self.width//2, self.height//2)
        self.mercator = Mercator(xres, yres, -179.9, -49.0, 179.9, 81.0)

        clock.schedule_interval(self.update,3.0)
        self.logString = 'Finding connections...' 
        self.logLabel = text.Label( self.logString,
                                    font_name=self.fontname,
                                    font_size=14,
                                    x=(self.width/2)-len(self.logString)*14,
                                    y=self.height-20,
                                    multiline=True,
                                    width=14*200)

        self.netstatString = ""
        self.netstatLabel = text.Label( "",
                            font_name=self.fontname,
                            font_size=self.fontsize,
                            x=0,
                            y=self.height-10,
                            multiline=True,
                            width=600)
        

        
        if self.foundLocalIp:
            self.IpCallback(self.localIp)
        else:
            self.getIpProcess = self.pool.apply_async(getExternalIp,callback=self.IpCallback)
            
            
        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            if buttons & mouse.LEFT:
                
                self.camera.x -= dx
                self.camera.y += dy

                width = (self.width/2)*(1.0/self.camera.zoom)
                height = (self.height/2)*(1.0/self.camera.zoom)

                if self.camera.x - width < 0:
                    self.camera.x = width
                if self.camera.x + width > self.width:
                    self.camera.x = self.width -width
                if self.camera.y - height < 0:
                    self.camera.y = height
                if self.camera.y +height > self.height:
                    self.camera.y = self.height-height
                self.calcPositions()
                
                
        @self.event
        def on_mouse_press(x, y, buttons, modifiers):
            if buttons & mouse.RIGHT:
                self.camera.x = self.width/2
                self.camera.y = self.height/2
                self.camera.zoom = 1.0
                self.calcPositions()
            if buttons & mouse.LEFT:
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                if self.debug:
                    print("CLICK", screen_to_model( (x, y, 0)))
                    
                    
        @self.event
        def on_mouse_scroll(x, y, sx, sy):
            self.camera.zoom += float(sy)*0.25
            if self.camera.zoom < 1.0:
                self.camera.zoom = 1.0
            self.calcPositions()
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            self.camera.zoomTo = screen_to_model((x, y, 0))
        @self.event
        def on_mouse_motion(x, y, dx, dy):
            self.mousePos = (x,y)
            self.checkHover()
        @self.event
        def on_key_press(symbol, modifiers):
            if symbol == key.SPACE:
                self.drawNetstatOverlay = not self.drawNetstatOverlay

        app.run()
        
        
        
    def usage(self):
        """
        Prompts the usage information when needed.
        """
        
        print("Usage: %s [option <arg>]\n" %(sys.argv[0]))
        print("-i <ipaddr> ,--ip=<ipaddr>                        external ip address of this machine")
        print(" --resolution=<width x height>                       resolution in pixel joined with an 'x'")
        print("-d, --debug                                       enable debug output")
        print("-v, --version                                     print version")

        sys.exit(1)

    def update(self, dt):
        new = [ x for x in getConnections() if x["remote"]  not in [y.data["remote"] for y in self.nodes if y.data["status"] != "CLOSE WAIT" ]]
        
        for i,n in enumerate(self.nodes):
            if n not in new:
                self.nodes[i].label.delete()
                self.nodes[i].hoverLabel.delete()
                self.nodes.pop(i)
        if self.debug:
            print("New Connections: %i" %(len(new)))
        for n in new:
            
            location =  self.geoIP.record_by_addr(n['remote'].split(':')[0].replace(' ',''))
            if location == None:
                if self.debug:
                    print("Cant locate %s\n" %(n['remote'].split(':')[0]))
                continue
                
            else:
                data = dict(n.items() + location.items())
                pos = self.mercator.screenCoords(data['latitude'], data['longitude'])
                self.nodes.append(Node(data,pos,self.labelBatch))
                
    
        if not self.foundLocalIp:
            self.logLabel.text = 'Trying to find external IP addres..'
        else:
            if not self.localNode:
                self.localNode = Node(self.localNodeData,self.localNodePos,self.labelBatch)
            self.localNode.connections = self.nodes

        self.netstatString = ""
        for n in self.nodes:
            self.netstatString += n.infoString+"\n"
        self.netstatLabel.text = self.netstatString


        self.calcPositions() 



    def IpCallback(self,arg):
        
        if arg != None:
            self.localIp = arg
            if self.debug:
                print('LocalIP %s' % self.localIp) 

            self.foundLocalIp = True
            data = self.geoIP.record_by_addr(self.localIp)
            if data != None:
                if self.debug:
                    print("Data:\n")
                    print("="*20)
                    print(data)
                data['ip'] = self.localIp
                data['remote'] = self.localIp
                data['local'] = self.localIp
                data['name'] = 'LOCALHOST'
                data['status'] = 'LOCALHOST'
                pos = self.mercator.screenCoords(data['latitude'],data['longitude'])
                
                self.localNodeData = data
                self.localNodePos = pos

                self.logLabel.text = ""
        else:
            self.logLabel.text = "Cant locate local IP Address"
            
            

    def checkHover(self):
    
        foundCount = 0
        foundNodes = []
        for i, n in enumerate(self.nodes):
            x, y = n.onScreen
            if(x-self.mousePos[0])**2 + (y-self.mousePos[1])**2 < 12**2:
                self.nodes[i].hover = True
                self.nodes[i].hoverLabel.text = self.nodes[i].hoverString
                foundCount+=1
                foundNodes.append(i)
            else:
                self.nodes[i].hover = False
                self.nodes[i].hoverLabel.text = ""
                self.nodes[i].expanded = False
        if self.localNode != None:
            x, y = self.localNode.onScreen
            if(x-self.mousePos[0])**2 + (y-self.mousePos[1])**2 < 12**2:
                self.localNode.hover = True
                foundCount+=1
            else:
                self.localNode.hover = False
        if foundCount > 1:
            self.expandMode = True

            offset =  (2.0*pi) /len(foundNodes) 
            
            for i,n in enumerate(foundNodes):
                if not self.nodes[n].expanded:
                    xoffset = cos(offset*i)*25*self.camera.zoom
                    yoffset = sin(offset*i)*25*self.camera.zoom
                    self.nodes[n].onScreen = (self.nodes[n].onScreen[0]+xoffset, self.nodes[n].onScreen[1]+yoffset )
                    self.nodes[n].label.x += xoffset
                    self.nodes[n].label.y += yoffset
                    self.nodes[n].hoverLabel.x += xoffset
                    self.nodes[n].hoverLabel.y += yoffset
                    self.nodes[n].expanded = True
        elif foundCount == 1:
            self.hovering = True
        else:
            self.expandMode = False
            self.hovering = False



    def calcPositions(self):
        if self.expandMode or self.hovering: #skip so we dont lose the expanded circle
            return
            
        self.camera.worldProjection()
        for i,n in enumerate(self.nodes):
            pos = model_to_screen((n.position[0], n.position[1], 0.0))
            self.nodes[i].onScreen = (pos[0].value, pos[1].value)
            self.nodes[i].label.x = pos[0].value
            self.nodes[i].label.y = pos[1].value+10#
            self.nodes[i].hoverLabel.x = pos[0].value+20
            self.nodes[i].hoverLabel.y = pos[1].value
            
        if self.localNode != None:
            pos = model_to_screen((self.localNode.position[0], self.localNode.position[1], 0.0) )
            self.localNode.onScreen = (pos[0].value, pos[1].value)   
            self.localNode.label.x = pos[0].value
            self.localNode.label.y = pos[1].value+10
            
    def drawNetstat(self):
        self.netstatLabel.draw()
    
    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.camera.worldProjection()
        self.batch.draw()

        self.camera.hudProjection()

        for n in self.nodes:
            n.draw()

        self.labelBatch.draw()

        if self.localNode != None:
            self.localNode.draw()
       
        if self.drawNetstatOverlay:
            self.drawNetstat()
        if self.debug:
            self.fps.draw()
        self.logLabel.draw()
        
        
    def loadSVGPaths(self, fileName,color,threshold=100.0):
        """ deprecated, parses svg path d attributes from tilemill exports """
        
        paths = pickle.load( open( fileName, 'rb') )
        print("Loaded %i points" % (len(paths)))

        self.points = []
        self.verts = []
        x,y = 0, 0
        for p in paths:
            batchpoints = []
            for cmd in p:
                if cmd[0] == 'M' or cmd[0] == 'm':
                    if self.debug:
                        print("Skipping %s"% cmd[0])
                    x, y = cmd[1], cmd[2]
                elif cmd[0] == 'L':

                    if (x-cmd[1])**2+(y-cmd[2])**2  < threshold**2:  # FIXME HARD

                        batchpoints.append(y)       
                        batchpoints.append(cmd[1])
                        batchpoints.append(cmd[2])     
                    else:
                        if self.debug:
                            print("SKIP")
                    x = cmd[1]
                    y = cmd[2]
                else:
                    print("unkown cmd %s"%cmd[0])
            numVerts = len(batchpoints)/2
            if self.debug:
                print("Batchlen:%i "%(numVerts))
            if numVerts > 0:
                self.batch.add( numVerts,
                                GL_LINES,
                                None,
                                ('v2f\static',batchpoints),
                                ('c3B\static',numVerts*color ) )

    def loadPaths(self,fileName,color):
        paths = pickle.load(open(fileName, "rb"))
        for p in paths:
            numPoints = len(p)
            scaledPoints = []
            for i in range(0,numPoints,2):
                scaledPoints.append(p[i]*self.width)
                scaledPoints.append(p[i+1]*self.height)

            l = len(scaledPoints)/2

            self.batch.add(l, GL_LINES, None,('v2f\static',scaledPoints),('c3B\static', l*color))

if __name__ == '__main__':
    na = NetArgos()


