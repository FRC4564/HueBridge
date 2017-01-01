import socket
from time import sleep
import json
try:
    import requests
except:
    import urequests as requests
    
# UPnP SSDP Search request header
HEADER = b"""M-SEARCH * HTTP/1.1\r
HOST: 239.255.255.250:1900\r
MAN: "ssdp:discover"\r
ST: ssdp:all\r
MX: 3\r
\r
"""

class Bridge:
    """Provides methods for connecting to and using Hue Bridge.  Supports
    Micropython, Python 2, and 3."""
    
    def __init__(self,autosetup=True, debug=1):
        self.debug = debug  #0=no prints, 1=messages, 2=debug
        self.IP = None
        self.username = None
        if autosetup:
            self.setup()


    def show(self,str,level=1):
        """ Show debug output. """
        if self.debug >= level:
            print(str)
            

    def setup(self):
        """ Loads bridge settings or attempts to establish them, if needed."""
        success = self.loadSettings()
        if success:
            # verify bridge settings work
            try:
                self.idLights()
                success = True
            except:
                success = False
        if not success:
            if self.discover():
                self.show('Bridge located at {}'.format(self.IP))
                self.show('>>> Press link button on Hue bridge to register <<<')
                if self.getUsername():
                    success = self.saveSettings()
                else:
                    self.show("Couldn't get username from bridge.")                
            else:
                self.show("Couldn't find bridge on LAN.")
        return success


    def discover(self):
        """ Locate Hue Bridge IP using UPnP SSDP search. Discovery will return
        when bridge is found or 3 seconds after last device response. Returns IP
        address or None."""
        #On ESP8266, disable AP WLAN to force use of STA interface
        #import network
        #ap = network.WLAN(network.AP_IF)
        #ap.active(False)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(HEADER, ('239.255.255.250',1900))    #UPnP Multicast
        s.settimeout(3)

        IP = None
        while IP == None:
            data, addr = s.recvfrom(1024)
            self.show(str(data),2)
            lines = data.split(b'\r\n')
            for l in lines:
                tokens = l.split(b' ')
                if tokens[0] == b'SERVER:':
                    product = tokens[3].split(b'/')
                    if product[0] == b'IpBridge':
                        IP = str(addr[0])
                        break

        s.close()
        self.IP = IP
        return IP


    def getUsername(self):
        """ Get a developer API username from bridge.
        Requires that the bridge link button be pressed sometime while polling.
        Polls for 20 seconds (20 attempts at 1 second intervals).
        Can timeout with error if bridge is non-responsive.
        Returns username on success or None on failure."""      
        url = 'http://{}/api'.format(self.IP)
        data = '{"devicetype":"TapLight#mydevice"}'
        username = None
        count = 20
        while count > 0 and username == None:
            resp = requests.post(url,data=data)
            if resp.status_code == 200:
                j = resp.json()[0]
                self.show(j,2)
                if j.get('success'):
                    username = str(j['success']['username'])
                    self.username = username
            sleep(1)
            count -= 1
        return username


    def saveSettings(self): 
        """ Save bridge IP and username to bridge.dat file.
        Returns True on success."""
        if self.IP and self.username:
            f=open('bridge.dat','w')
            f.write(json.dumps([self.IP,self.username]))
            f.close()
            return True
        else:
            return None


    def loadSettings(self):
        """ Load bridge IP and username from bridge.dat file and set base URL.
        Returns True on success. """
        try:
            f=open('bridge.dat')
        except:
            return None
        l = json.load(f)
        f.close()
        self.IP = str(l[0])
        self.username = str(l[1])
        self.show('Loaded settings {} {}'.format(self.IP,self.username),2)
        return True


    def resetSettings(self):
        """Delete current saved bridge settings and reinitiate."""
        from os import remove
        remove('bridge.dat')
        self.IP = None
        self.username = None
        self.setup()
        

    def url(self,path):
        """Return url for API calls."""
        return 'http://{}/api/{}/{}'.format(self.IP,self.username,path)


    def get(self, path):
        """Perform GET request and return json result."""
        url = self.url(path)
        self.show(url,2)
        resp = requests.get(url).json()
        self.show(resp,2)
        return resp


    def put(self, path, data):
        """Perform PUT request and return response."""
        url = self.url(path)
        self.show(url,2)
        data = json.dumps(data)
        self.show(data,2)
        resp = requests.put(url, data=data).json()
        self.show(resp,2)
        return resp


    def allLights(self):
        """Returns dictionary containing all lights, with detail."""
        """Large return set, not ideal for controllers with limited RAM."""
        return self.get('lights')


    def idLights(self):
        """Returns list of all light IDs."""
        ids = self.get('groups/0')['lights']
        for i in range(len(ids)):
            ids[i] = int(ids[i])
        return ids


    def getLight(self,id):
        """Returns dictionary of light details for given ID."""
        return self.get('lights/{}'.format(str(id)))


    def getLights(self):
        """Iterates through each light to build and return a dictionary 
        of light IDs and names."""
        dict = {}
        for i in self.idLights():
            dict[i] = str(self.getLight(i)['name'])
        return dict
            

    def setLight(self,id,**kwargs):
        """Set one or more states of a light.  
        Ex: setLight(1,on=True,bri=254,hue=50000,sat=254)"""
        self.put('lights/{}/state'.format(str(id)),kwargs)


    def allGroups(self):
        """Returns dictionary containing all groups, with detail."""
        return self.get('groups')


    def getGroup(self,id):
        """Returns dictionary of group details."""
        return self.get('groups/{}'.format(str(id)))


    def getGroups(self):
        """Returns dictionary of group IDs and names."""
        dict = {}
        groups = self.allGroups()
        for g in groups:
            dict[int(g)] = str(groups[g]['name'])
        return dict
    

    def setGroup(self,id,**kwargs):
        """Set one or more states of a group.
        Ex: setGroup(1,bri_inc=100,transitiontime=40)"""
        self.put('groups/{}/action'.format(str(id)),kwargs)
        
      
