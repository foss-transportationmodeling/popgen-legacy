from __future__ import with_statement

import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *



class Geocorr(object):
    def __init__(self, userprov=None, geocorrLocation=""):
        self.userProv = userprov
        self.location = geocorrLocation
        
class Sample(object):
    def __init__(self, userprov=None, sampleHHLocation="", sampleGQLocation="", samplePersonLocation=""):
        self.userProv = userprov
        self.hhLocation = sampleHHLocation
        self.gqLocation = sampleGQLocation
        self.personLocation = samplePersonLocation

class Control(object):
    def __init__(self, userprov=None, controlHHLocation="", controlGQLocation="", controlPersonLocation=""):
        self.userProv = userprov
        self.hhLocation = controlHHLocation
        self.gqLocation = controlGQLocation
        self.personLocation = controlPersonLocation
        
class DBInfo(object):
    def __init__(self, hostname="", username="", password="", driver="QMYSQL"):
        self.driver = driver
        self.hostname = hostname
        self.username = username
        self.password = password

class NewProject(object):
    def __init__(self, name="", location="", description="", 
                 region="", state="", countyCode="", stateCode="", stateAbb="", 
                 resolution="", geocorrUserProv=Geocorr(), 
                 sampleUserProv=Sample(), controlUserProv=Control(), 
                 db = DBInfo()):
        self.name = name
        self.location = location
        self.description = description
        self.region = region
        self.state = state
        self.countyCode = countyCode
        self.stateCode = stateCode
        self.stateAbb = stateAbb
        self.resolution = resolution
        self.geocorrUserProv = geocorrUserProv
        self.sampleUserProv = sampleUserProv
        self.controlUserProv = controlUserProv
        self.db = db


    def save(self):
        with open('%s/%s/%s.pop' %(self.location, self.name, self.name), 
                  'wb') as f:
            pickle.dump(self, f, True)
        pass

    def update(self):
        pass




            
            
    
        
