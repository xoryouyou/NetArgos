import cPickle as pickle

def loadSVGPaths( fileName,xres,yres,threshold=100.0):
    debug = True
    paths = pickle.load( open( fileName, 'rb') )
    print("Loaded %i points" % (len(paths)))

    points = []
    verts = []
    x,y = 0, 0
    for p in paths:
        batchpoints = []
        for cmd in p:
            if cmd[0] == 'M' or cmd[0] == 'm':
                if debug:
                    print("Skipping %s"% cmd[0])
                x, y = cmd[1], cmd[2]
            elif cmd[0] == 'L':
                # ugly fix for crossiong lanes from greenland to mexico and
                # stuff
                if (x-cmd[1])**2+(y-cmd[2])**2  < threshold**2:  # FIXME HARD

                    batchpoints.append(x/xres)
                    batchpoints.append(y/yres)       
                    
                    batchpoints.append(cmd[1]/xres)
                    batchpoints.append(cmd[2]/yres)     

                x = cmd[1]
                y = cmd[2]

        if len(batchpoints) > 0:
            print("appending ",len(batchpoints))
            points.append(batchpoints)

                            
    return points
if __name__ == '__main__':
    points = loadSVGPaths('borders-50.pickle',1920.0,1080.0,threshold=300.0)
    pickle.dump(points, open("borders-50-batched.bin","wb"))
    points = loadSVGPaths('coast-50.pickle',1920.0,1080.0,threshold=300.0)
    pickle.dump(points, open("coast-50-batched.bin","wb"))
