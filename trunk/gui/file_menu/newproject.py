from __future__ import with_statement
from collections import defaultdict

import pickle, numpy

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


class SelectedVariableDicts(object):
    def __init__(self, hhldVariables=defaultdict(dict), gqVariables=defaultdict(dict), personVariables=defaultdict(dict)):
        self.hhld = hhldVariables
        self.gq = gqVariables
        self.person = personVariables




class Geography(object):
    def __init__(self, state, county, tract, bg, puma5=None):
        self.state = state
        self.county = county
        self.tract = tract
        self.bg = bg
        self.puma5 = puma5
        
    """
    def gqControlVariables(self):
        pass

    def hhldControlVariables(self):
        pass

    def personControlVariables(self):
        pass

    def gqDimensions(self):
        pass

    def hhldDimensions(self):
        pass

    def personDimensions(self):
        pass
    

    def runIPFHousingNoAdj(self):
        #return objective freq
        pass

    def runIPFHousingWithAdj(self):
        #return constraint freq
        pass

    def runIPFGqNoAdj(self):
        #return objective freq
        pass

    def runIPFGqWithAdj(self):
        #return constraint freq
        pass

    def runIPFPersonNoAdj(self):
        #return objective freq
        pass

    def runIPFPersonWithAdj(self):
        #return constraint freq
        pass


    def constraints(self):
        pass

    def runIPU(self):
        pass


    def createSynPop(self):
        pass

    def writeSynPop(self):
        pass

    """

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
                 db=DBInfo(), parameters=Parameters(), controlVariables=SelectedVariableDicts(),
                 hhldVars=None, hhldDims=None, gqVars=None, gqDims=None, personVars=None, personDims=None, geoIds={}):
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
        self.selVariableDicts = controlVariables
        self.hhldVars = hhldVars
        self.hhldDims = hhldDims
        self.gqVars = gqVars
        self.gqDims = gqDims
        self.personVars = personVars
        self.personDims = personDims
        self.synGeoIds = geoIds

    def save(self):
        if len(self.filename) < 1:
            self.filename = self.name
            print 'filename - %s' %self.filename
            print 'name - %s' %self.name

        with open('%s/%s/%s.pop' %(self.location, self.name, self.filename),
                  'wb') as f:
            pickle.dump(self, f, True)


    def update(self):
        pass


if __name__ == "__main__":
    a = ControlVariable()

    print dir(a)
    print type(a)



