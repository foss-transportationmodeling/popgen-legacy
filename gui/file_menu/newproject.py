from __future__ import with_statement
from collections import defaultdict

import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui.global_vars  import *



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


class ProjectControlVariables(object):
    def __init__(self, hhldVariables=defaultdict(dict), gqVariables=defaultdict(dict), personVariables=defaultdict(dict)):
        self.hhldVariables = hhldVariables
        self.gqVariables = gqVariables
        self.personVariables = personVariables


class Parameters(object):
    def __init__(self, 
                 ipfTol=IPF_TOLERANCE, 
                 ipfIter=IPF_MAX_ITERATIONS, 
                 ipuTol=IPU_TOLERANCE, 
                 ipuIter=IPU_MAX_ITERATIONS, 
                 synPopDraws=SYNTHETIC_POP_MAX_DRAWS, 
                 synPopPTol=SYNTHETIC_POP_PVALUE_TOLERANCE):

        self.ipfTol = ipfTol
        self.ipfIter = ipfIter
        self.ipuTol = ipuTol
        self.ipuIter = ipuIter
        self.synPopDraws = synPopDraws
        self.synPopPTol = synPopPTol



class NewProject(object):
    def __init__(self, name="", filename="", location="", description="",
                 region="", state="", countyCode="", stateCode="", stateAbb="",
                 resolution="", geocorrUserProv=Geocorr(),
                 sampleUserProv=Sample(), controlUserProv=Control(),
                 db=DBInfo(), parameters=Parameters()):
        self.name = name
        self.filename = name
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
        self.parameters = parameters

    def save(self):
        if len(self.filename) < 1:
            self.filename = self.name
            print 'filename - %s' %self.filename
            print 'name - %s' %self.name

        with open('%s/%s/%s.pop' %(self.location, self.name, self.filename),
                  'wb') as f:
            pickle.dump(self, f, True)
        pass

    def update(self):
        pass








