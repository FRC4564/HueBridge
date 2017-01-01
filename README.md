# HueBridge
An easy to use, micropython-compatible class to access and control lights on a Philips Hue Bridge.

## Features
* Discovers bridge using the UPnP SSDP protocol
* Handles developer API username registration for API access
* Stores bridge IP and username for instant access on restarts
* Simple methods to get lists of lights and groups
* Set one or many light or group state parameters with a single call
* Works equally well in micropython or python 2.7 and up
* Easy to extend with new methods to access more bridge functions

## Usage
The first time the `Bridge` class is used, it will discovery the bridge and then initiate the necessary API username registration. 
```
import hue
h = hue.Bridge()
```
You'll be prompted to press the link button on the Hue Bridge.
```
Bridge located at 192.168.0.7
>>> Press link button on Hue bridge to register <<<
```
**If you are using the ESP8266, you'll need to disable the AP WLAN interface for the discovery process to work.**  This also requires that the STA WLAN (station) interface be connected to the same network as the bridge.  Here's how to disable the AP WLAN interface.
```
import network
ap=network.WLAN(network.AP_IF)
ap.active(False)
```
Once you've connected to the bridge, you can interact with *lights* and *groups*.  Individual lights or groups are referenced by an ID number.  You can get the list of IDs with the methods `getLights` and `getGroups'.
```
h.getGroups()
{1: 'Dining room', 2: 'Bedroom', ... , 9: 'Porch', 10: 'Spare bedroom'}
```
To get details about a specific light our group, use the `getLight` and `getGroup` methods.
```
h.getLight(1)
{u'name': u'Dining 1', u'swversion': u'5.38.2.19136', u'manufacturername': u'Philips', u'state': {u'on': True, u'reachable': True, u'bri': 200, u'alert': u'none'}, u'uniqueid': u'00:17:88:01:10:40:2c:14-0b', u'type': u'Dimmable light', u'modelid': u'LWB006'}
```
Here's an example of how you access individual settings from the response:
```
light = h.getLight(1)
light['state']['on']
True
light['state']['bri']
200
```
To set light or group states use the `setLight` and `setGroup` methods.
```
h.setLight(1,bri=254,transitiontime=20)
h.setGroup(10,on=False)
h.setLight(2,bri_inc=-100)
```

## Installation
Just download the `hue.py` file from this repository and place in a folder with your python code.

## More In-Depth Info
If you'd like to know more about the Hue Bridge API, head over to [https://developers.meethue.com/philips-hue-api].  You'll need to register as a developer to gain access, which is free.

You can use the `get()` and `put()` methods to access other aspects of the bridge API. For example, to get bridge configuration along with the current whitelist of usernames, try the folowing:.
```
h.get('config')
```
The methods `post()` and `delete()` are not currently implemented, but can be easily added, by modelling them after the get and put methods.

When you first use this class, it runs `setup()`, which locates the bridge's IP address and then follows-up with getting a developer username from the bridge.  Both of these values will be stored to the file `bridge.dat` within the current working directory.  The next time you use the Bridge class, it will load the saved IP and username values.
If the bridge changes IP, you can edit the `bridge.dat` file.  It is recommended that you make reserve the bridges IP address on your router, so it doesn't hop around. Alternatively, you can force a `discover()` whenever you connect to the bridge.  To do this you'll need to disable autosetup when instantiating the Bridge class. Here's the steps necessary:
```
h = hue.Bridge(autosetup=False)
h.loadSettings()   #This will load the last known IP and API Username
h.discover()       #Find the bridge's current IP
h.saveSettings()   #Optionally, you can save the updated IP
```

## Troubleshooting
If you are having trouble with the saved settings and would just like to start fresh, call the `reset()` method.  The IP discovery and username process will take place, and the new settings will be saved.  
```
h = hue.Bridge(autosetup=False)
h.reset()   #Clear saved settings
```
You need to throttle how quickly you set light or group parameters.  Philips suggest that lights be updated no quicker than 10 times per second, and groups be updated at most, once per second.  These are just guidelines, to follow.  It is also best practice to minimize how many state values you change in each call.  For instance, once the light is 'on', you can adjust brightness in successful calls, without setting 'on' again.
