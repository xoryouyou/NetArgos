import getopt
import sys

version = '1.0'
debug = False
ip = '0.0.0.0'

print 'ARGV      :', sys.argv[1:]
try:

    options, remainder = getopt.getopt(sys.argv[1:], 'i:v', ['ip=', 
                                                         'debug',
                                                         'version',
                                                         'resolution=',
                                                         ])
except getopt.GetoptError ,e:
    print("FAIL")
else:
    print 'OPTIONS   :', options

    for opt, arg in options:
        if opt in ('-i','--ip'):
            ip = arg
        elif opt in ('-v', '--version'):
            version = 2.0
        elif opt == '--debug':
            debug = True
        elif opt == '--resolution':
            if 'x' in arg:
                x,y = arg.split('x')
                x = int(x)
                y = int(y)
                print(x,y)
            else:
                print("RESOLUTION WITH 'x' MOTHERFUCKER")
            
        else:
            print("DUNNO")
    print 'VERSION   :', version
    print 'DEBUG     :', debug
    print 'IP        :', ip
    print 'REMAINING :', remainder
    print 'RESOLUTION:',x,y


