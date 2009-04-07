from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os, sys

from gui.global_vars import *

from gui.misc.dbf import *

qgis_prefix = "C:/qgis"

# This class generates the follwing results after a population synthesizer run
# A point layer where each point is a synthesized household
# An output file containing aards and pvalues for the whole region
# An output file containing HH and PP attributes (synthetic and actual) for the whole region
# An output file containing the persontype frequencies (synthetic and actual) for each small geography

hhcount_fieldname = "HHFREQ"

class ResultsGen():
    def __init__(self, project):
        self.project = project

        self.name = self.project.name
        self.resultsloc = self.project.location + os.path.sep + self.name + os.path.sep + "results"
        self.resultsloc = os.path.realpath(self.resultsloc)
        self.mapsloc = DATA_DOWNLOAD_LOCATION + os.path.sep + self.project.state + os.path.sep + 'shapefile'
        self.mapsloc = os.path.realpath(self.mapsloc)
        self.stateCode = self.project.stateCode[self.project.state]
        self.countyCodes=[]
        
        for i in self.project.region.keys():
            county = i + ',' + self.project.state
            self.countyCodes.append(self.project.countyCode['%s' %county])

        if self.project.resolution == "County":
            self.res_prefix = "co"

        if self.project.resolution == "Tract":
            self.res_prefix = "tr"

        if self.project.resolution == "Blockgroup":
            self.res_prefix = "bg"

        print self.name
        print self.resultsloc        
        print self.mapsloc
        print self.stateCode
        print self.countyCodes
        print self.res_prefix

        #self.resultsloc = "C:/populationsynthesis/gui/results"
        #self.mapsloc = "C:/populationsynthesis/gui/data"
        #self.state = "04"
        #self.counties = ["015", "005", "017", "025"]

    
    def downloadShapeFiles(self):
        pass

    def extractShapeFiles(self):
        pass

    def generate(self):
        self.create_hhmap()
        self.create_regstats()
        self.create_indstats()
    
    def create_hhmap(self):
        # create a new shapefile with selected counties
        self.makesublayer() 
        # Decide whether to show points or not
    
    def makesublayer(self):
        folder = res_prefix+self.stateCode+"_d00_shp"
        filename = res_prefix+self.stateCode+"_d00.shp"
        filedbf = res_prefix+self.stateCode+"_d00.dbf"
        fileshx = res_prefix+self.stateCode+"_d00.shx"
              
        basefile = self.mapsloc+os.path.sep+folder+os.path.sep+filename
        basedbf = self.mapsloc+os.path.sep+folder+os.path.sep+filedbf
        baseshx = self.mapsloc+os.path.sep+folder+os.path.sep+fileshx
        
        newfilename = res_prefix+self.stateCode+"_selected"  
        newfile = self.resultsloc+os.path.sep+newfilename + ".shp"
        newdbf = self.resultsloc+os.path.sep+newfilename + ".dbf"
        newshx = self.resultsloc+os.path.sep+newfilename + ".shx"   
        
        baselayer = QgsVectorLayer(basefile, "all", "ogr")
        baseprovider = baselayer.getDataProvider()
        
        allAttrs = baseprovider.allAttributesList()
        countyindex = baseprovider.indexFromFieldName("COUNTY")
        baselayer.select(QgsRect(), True)
        feat = QgsFeature()
        
        if os.path.exists(newfile):
            os.remove(newfile)
        if os.path.exists(newdbf):
            os.remove(newdbf)
        if os.path.exists(newshx):
            os.remove(newshx)
            
        writer = QgsVectorFileWriter(newfile, "CP1250", baseprovider.fields(), QGis.WKBPolygon, None)
        del writer
        f = open(basedbf, 'rb')
        db = list(dbfreader(f))
        f.close()
        fieldnames, fieldspecs, records = db[0], db[1], db[2:]
        f = open(newdbf, 'rb')
        db = list(dbfreader(f))
        f.close()
        fieldnames2, fieldspecs2, records2 = db[0], db[1], db[2:]
        f = open(newdbf, 'wb')
        dbfwriter(f, fieldnames2, fieldspecs, records2)
        f.close()
        
        newlayer = QgsVectorLayer(newfile, "selected", "ogr")
        newlayer.startEditing()
        newprovider = newlayer.getDataProvider()
        
        
        while baseprovider.getNextFeature(feat):
           attrMap = feat.attributeMap()
           featcounty = attrMap[countyindex].toString().trimmed()
           if featcounty in self.countyCodes:
               featid = feat.featureId()
               selfeat = QgsFeature()
               baselayer.getFeatureAtId(featid, selfeat)
               newlayer.addFeature(selfeat)
        newlayer.commitChanges()
       
        f = open(newdbf, 'rb')
        db = list(dbfreader(f))
        f.close()
        fieldnames, fieldspecs, records = db[0], db[1], db[2:]
        fieldnames.append(hhcount_fieldname)
        fieldspecs.append(('N',11,0))
        for rec in records:
            rec.append(0)
            #rec.append(self.getHHFreq())
        f = open(newdbf, 'wb')
        dbfwriter(f, fieldnames, fieldspecs, records)
        f.close()
        #ctyidx = fieldnames.index("COUNTY")
        #records2 = []
        #for rec in records:
        #    if rec[ctyidx] in self.countyCodes:
        #        records2.append(rec)
                
        
        #f = open(newdbf, 'wb')
        #dbfwriter(f, fieldnames, fieldspecs, records)
        #f.close()
        
        

    def create_regstats(self):
        pass
    
    def create_indstats(self):
        pass

if __name__ == "__main__":
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    test = ResultsGen()
    test.generate()
    
