from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sys, os
import shutil

#from dbfpy import dbf
from dbf import *

from gui.file_menu.intro_toolbar import *
from doRandPoints import *


qgis_prefix = "C:/qgis"

# Inputs for this module

project_location = "C:/populationsynthesis/gui/results"
inlayer_loc = "./data/county.shp"
selectlist = [["04", "015"],["04", "005"],["04", "017"], ["04", "025"]]

hhcount_fieldname = "hhfreq"

class Results(QDialog):
    def __init__(self, parent=None):
        super(Results, self).__init__(parent)
        self.setFixedSize(QSize(800,500))

    # Displaying counties and selecting counties using the map
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(200,200,255))
        self.canvas.enableAntiAliasing(True)
        self.canvas.useQImageToRender(False)
        
        layerName = "Counties"
        layerProvider = "ogr"
        self.layer  = QgsVectorLayer(inlayer_loc, layerName, layerProvider)
        if not self.layer.isValid():
            return
        
        #modlayer = 
        self.outSelectGeogs()   
        self.addLayer(self.layer)
        self.addLayer(self.geoglayer)
        self.canvas.setExtent(self.layer.extent())
        
        
        #QgsMapLayerRegistry.instance().addMapLayer(self.geoglayer)
        #QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        
        #self.canvas.setExtent(self.layer.extent())
        #gl = QgsMapCanvasLayer(self.layer)
        #hl = QgsMapCanvasLayer(self.geoglayer)
        #layers = [gl,hl]
        #self.canvas.setLayerSet(layers)

        self.toolbar = Toolbar(self.canvas, self.geoglayer)
        vLayout = QVBoxLayout()
        vLayout.addWidget(self.toolbar)
        vLayout.addWidget(self.canvas)
        self.setLayout(vLayout)
    
    def outSelectGeogs(self):
        sel_ids = []
        sel_feats = []
        for geogid in selectlist:
            featid = self.getFeatId(geogid)
            sel_ids.append(featid)
            feat = QgsFeature()
            self.layer.getFeatureAtId(featid, feat)
            sel_feats.append(feat)
        print sel_ids
        
        basepath = inlayer_loc.split('.shp')
        dbfpath = basepath[0] + '.dbf'
        fdst = basepath[0] + '_test' + '.shp'
        QgsVectorFileWriter.deleteShapeFile(fdst)
        provider = self.layer.getDataProvider()
        writer = QgsVectorFileWriter(fdst, "CP1250", provider.fields(), QGis.WKBPolygon, None)
        del writer
        newlayer = QgsVectorLayer(fdst,"SelCounties", "ogr")
        newlayer.startEditing()
        newlayer.addFeatures(sel_feats)
        newlayer.commitChanges()
        print newlayer.featureCount()
        self.setGeogLayer(newlayer)

        
    def getFeatId(self, id):
        state = id[0]
        county = id[1]
        provider = self.layer.getDataProvider()
        allAttrs = provider.allAttributesList()

        stidx = provider.indexFromFieldName("STATE")
        ctindx = provider.indexFromFieldName("COUNTY")
        
        #self.layer.setSelectedFeatures(range(self.layer.featureCount()))
        self.layer.select(QgsRect(), True)
        #provider.select(allAttrs, QgsRect(), False)
        feat = QgsFeature()
        while provider.getNextFeature(feat):
            attrMap = feat.attributeMap()
            featstate = attrMap[stidx].toString().trimmed()
            featcounty = attrMap[ctindx].toString().trimmed()
            if (featstate.compare(state) == 0 and featcounty.compare(county) == 0):
                return feat.featureId()
        return -1

        #print self.layer.selectedFeaturesIds()
    def setGeogLayer(self, layer):
        self.geoglayer = layer

    def addLayer(self, layer):
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        cl = QgsMapCanvasLayer(layer)
        layers = [cl]
        self.canvas.setLayerSet(layers)
    
    def out(self):
        layerpath = inlayer_loc
        layerName = "Counties"
        layerProvider = "ogr"
        layer = QgsVectorLayer(layerpath, layerName, layerProvider)
        if not layer.isValid():
            return
        
        basepath = inlayer_loc.split('.shp')
        dbfpath = basepath[0] + '.dbf'
        
        provider = layer.getDataProvider()
        allAttrs = provider.allAttributesList()
        
        
        
        allFields = provider.fields()
        for(i, field) in allFields.iteritems():
            print field.name()
        
        fdst = basepath[0] + '_test' + '.shp'
        QgsVectorFileWriter.deleteShapeFile(fdst)
        QgsVectorFileWriter.writeAsShapefile(layer, fdst, "CP1250")
        
        if not self.isFieldInTable(hhcount_fieldname,allFields):
            print "Field Absent"
            #db = dbf.Dbf(dbfpath)
            #db.addField("hhcount_fieldname", 'N',10,0)
            #for rec in db:
                #print rec
            f = open(dbfpath, 'rb')
            db = list(dbfreader(f))
            f.close()
            fieldnames, fieldspecs, records = db[0], db[1], db[2:]

            fieldnames.append(hhcount_fieldname)
            fieldspecs.append(('N',11,0))
            
            for rec in records:
                rec.append(0)
                       
            f = open(dbfpath, 'wb')
            dbfwriter(f, fieldnames, fieldspecs, records)


            
            provider.select(allAttrs, QgsRect())
            
            #print provider.featureCount()
            feat = QgsFeature()
            
            #copyfeatures = []
            print "Old Features Count"
            print provider.featureCount()
            
            #while provider.getNextFeature(feat):
            #    feat.addAttribute(12, QVariant(hhcount_fieldname))
            #    copyfeatures.append(feat)

            #provider.deleteFeatures(range(provider.featureCount()))
            #layer.commitChanges()
            #provider.deleteFeatures([i])
            
            #provider.addAttributes( {hhcount_fieldname : "OFTInteger"})
            
            #provider.addFeatures(copyfeatures)

            
        print provider.fieldCount()


    
    def isFieldInTable(self, field, allFields):
        retval = False
        for (i, attr) in allFields.iteritems():
            if attr.name().trimmed() == field:
                retval = True
                return retval
        return retval
        


def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    res = Results()
    res.out()


#    res.show()
#    app.exec_()

    QgsApplication.exitQgis()


if __name__ == "__main__":
    main()

