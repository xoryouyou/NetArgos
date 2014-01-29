'''

netutil.py: NetArgos (c) 2013 Kabelmaulwurf

This file is part of NetArgos.

NetArgos.py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

NetArgos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

'''


"""
    A collection of network utilities to gather information.
"""

from socket import gethostbyname, gethostname, setdefaulttimeout
from urllib import urlopen
from time import sleep
from re import findall
import psutil

def getInternalIp():
    """
    A function to return the local IP-Address.
    
    """
    
    return gethostbyname("%s.local" % gethostname())

def getExternalIp():
    """
    A function to get the external IP-Address via checkip.dyndns.org
    
    :rtype: string '123.123.123.123' or None
    
    """
    
    tries = 3
    delay = 2
    setdefaulttimeout(delay)
    while tries:
        try:
            site = urlopen("http://checkip.dyndns.org/")
        except Exception as e:
            print("Trying to get ip...%i tries left %s"%(tries,e))

            tries -= 1
            sleep(delay)
        else:

            grab = findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', site.read())
            if grab == []:
                return None
            else:
                return grab[0]
    return None

def getConnections():
    """
    Gathers the network information from every process via psutil.
    
    :rtype: list of dictionaries containing the information
    """
    
    ret = []
    for p in psutil.process_iter():
        try:
            name = p.name
            cons = p.get_connections(kind='inet')
        except psutil.AccessDenied:
            pass
        else:
            for c in cons:
                if c.remote_address and c.remote_address[0] != '127.0.0.1' and c.remote_address[0] != '0.0.0.0':

                    d = {'local':'.'.join( [str(i).rjust(3) for i in c.local_address[0].split('.')] )+":"+str(c.local_address[1]).rjust(5),
                         'remote' : '.'.join( [str(i).rjust(3) for i in c.remote_address[0].split('.')] )+":"+str(c.remote_address[1]).rjust(5),
                         'status':str(c.status).center(15),
                         'pid':p.pid,
                         'name':name[:15]}
                    ret.append(d)
    return ret
