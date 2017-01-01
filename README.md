# HueBridge
An easy to use, micropython-compatible class to access and control lights on a Phillips Hue Bridge.

## Features
* Discovers bridge using UPnP SSDP protocol
* Handles developer API username registration for API access
* Stores bridge IP and username for instant access on restarts
* Simple methods to get list of lights and groups
* Set one or many light or group state parameters with a single call
* Works equally well in micropython or python 2.7 and up
* Provides basic methods for working with Lights and Groups
* Easy to extend with new methods to access more bridge functions

## Usage
The first time the `Bridge` class is used, it will discovery the bridge and then initiate the username registration. 
```
import hue
h = hue.Bridge()
```
When prompted, press the link button on the Hue Bridge. 
```
Bridge located at 192.168.0.7
>>> Press link button on Hue bridge to register <<<
```
**If you are using the ESP8266, you'll need to disable to AP WLAN interface for the discovery to work.**  This also requires that the STA WLAN interface to connected to the same network as the bridge.  Here's how to disable the AP WLAN interface.
```
import network
ap=network.WLAN(network.AP_IF)
ap.active(False)
```
Once you've connected to the bridge, you can interact with Lights and Groups.  Individual lights or groups are referenced by an ID number.  You can get the list of IDs with the methods `getLights` and `getGroups'
```
h.getGroups()
{1: 'Dining room', 2: 'Bedroom', ... , 9: 'Porch', 10: 'Spare bedroom'}
```
To get details about a light our group, use the `getLight` and `getGroup` methods and provide an ID.
```
h.getLight(1)
{u'name': u'Dining 1', u'swversion': u'5.38.2.19136', u'manufacturername': u'Philips', u'state': {u'on': True, u'reachable': True, u'bri': 200, u'alert': u'none'}, u'uniqueid': u'00:17:88:01:10:40:2c:14-0b', u'type': u'Dimmable light', u'modelid': u'LWB006'}
```
Access specific settings as follows:
```
light = h.getLight(1)
light['state']['on']
True
light['state']['bri']
200
```
To set light and group states use the `setLight` and `setGroup` methods.
```
h.setLight(1,Bri=254,transitiontime=20)
h.setGroup(1,on=False)
```

##Installation
Just download the `hue.py` file from this repository and place in a folder with your python code.
