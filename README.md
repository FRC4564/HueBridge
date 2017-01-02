# Hue Bridge Client
An easy-to-use, MicroPython-compatible class to access and control lights on a Philips Hue Bridge.

## Features
* Automatic bridge discovery using the UPnP SSDP protocol
* Handles developer API username registration for API access
* Stores bridge IP and username for instant access on restarts
* Simple methods to get lists of lights and groups
* Set one or many, light or group state parameters with a single call
* Works equally well in micropython or python 2.7 and up
* Easy to extend with new methods to access more bridge functionality

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
Once you've connected to the bridge, you can interact with *lights* and *groups*.  Individual lights or groups are referenced by an ID number.  You can get the list of IDs with the methods `getLights` and `getGroups`.
```
h.getGroups()
{1: 'Dining room', 2: 'Bedroom', ... , 9: 'Porch', 10: 'Spare bedroom'}
```
To get details about a specific light our group, use the `getLight` and `getGroup` methods.
```
h.getLight(1)
{u'name': u'Dining 1', u'swversion': u'5.38.2.19136', u'manufacturername': u'Philips', u'state': {u'on': True, u'reachable': True, u'bri': 200, u'alert': u'none'}, u'uniqueid': u'00:17:88:01:10:40:2c:14-0b', u'type': u'Dimmable light', u'modelid': u'LWB006'}
```
Here's an example of how to access individual settings from the response:
```
light = h.getLight(1)
light['state']['on']
True
light['state']['bri']
200
```
To set light or group state parameters use the `setLight` and `setGroup` methods.
```
h.setLight(1,bri=254,transitiontime=20)
h.setGroup(10,on=False)
h.setLight(2,bri_inc=-100)
```

## Installation
Just download the `hue.py` file from this repository and place in a folder with your python code.

## More In-Depth Info
If you'd like to know more about the Hue Bridge API, head over to [https://developers.meethue.com/philips-hue-api].  You'll need to register as a developer to gain access, which is free.

To access other aspects of the bridge API, use the `get()` and `put()` methods. For example, to get bridge configuration along with the current whitelist of usernames, try the folowing:
```
h.get('config')
```
The methods `post()` and `delete()` are not currently implemented, but can be easily added, by modelling them after the get and put methods.  These methods are used to change bridge and device configurations.

When first instantiating this class, `setup()` runs, which locates the bridge's IP address and attempts to get an API username from the bridge.  Both of these values will be stored to the file `bridge.dat` within the current working directory.  The next time the Bridge class instantiated, it will load the saved IP and username values automatically.
If the bridge changes IP, you can edit the `bridge.dat` file.  It is recommended that you reserve the bridges IP address on your router, so it doesn't hop around. Alternatively, you can force a `discover()` whenever you connect to the bridge to get its current IP.  To do this you'll need to disable autosetup when instantiating the Bridge class. Here's the steps necessary:
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
If you are having get the bridge to respond to commands, enable *debug* level 2 to get feedback from the method calls.
```
h = hue.Bridge(debug=2)    #Enable debug output
```
Be aware that issuing *set* commands too quickly can lead to the bridge refusing to process the request.  Philips suggest that lights be updated no quicker than 10 times per second and groups be updated, at most, once per second.  These are just guidelines to follow.  It is also best practice to minimize how many state values you change in each call.  For instance, once the light is 'on', you can adjust brightness, in successive calls, without setting 'on' again.
