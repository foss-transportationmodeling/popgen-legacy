#-----------------------------------------------------------
# 
# Generate Random Points
#
# A QGIS plugin for generating a simple random points
# shapefile. 
#
# Copyright (C) 2008  Carson Farmer
#
# EMAIL: carson.farmer (at) gmail.com
# WEB  : www.geog.uvic.ca/spar/carson
#
#-----------------------------------------------------------
# 
# licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from random import *
import math

class RandPoints():
    def __init__(self):
        
        self.iface = iface
        self.setupUi(self)
        QObject.connect(self.toolOut, SIGNAL("clicked()"), self.outFile)
        QObject.connect(self.inShape, SIGNAL("currentIndexChanged(QString)"), self.update)
        self.progressBar.setValue(0)
        self.setWindowTitle("Random points")
        mapCanvas = self.iface.getMapCanvas()
        for i in range(mapCanvas.layerCount()):
            layer = mapCanvas.getZpos(i)
            if (layer.type() == layer.VECTOR and layer.vectorType() == QGis.Polygon) or layer.type() == layer.RASTER:
            	self.inShape.addItem(layer.name())

# If input layer is changed, update field list            		
    def update(self, inputLayer):
        self.cmbField.clear() 
        changedLayer = self.getMapLayerByName(inputLayer)
        if changedLayer.type() == changedLayer.VECTOR:
        	self.rdoStratified.setEnabled(True)
        	self.rdoDensity.setEnabled(True)
        	self.rdoField.setEnabled(True)
        	self.label_4.setEnabled(True)
        	changedLayer = self.getVectorLayerByName(inputLayer)
        	changedFields = self.getFieldList(changedLayer)
        	for i in changedFields:
        		self.cmbField.addItem(unicode(changedFields[i].name()))
        else:
        	self.rdoUnstratified.setChecked(True)
        	self.rdoStratified.setEnabled(False)
        	self.rdoDensity.setEnabled(False)
        	self.rdoField.setEnabled(False)
        	self.spnStratified.setEnabled(False)
        	self.spnDensity.setEnabled(False)
        	self.cmbField.setEnabled(False)
        	self.label_4.setEnabled(False)

# when 'OK' button is pressed, gather required inputs, and initiate random points generation            
    def accept(self):
	if self.inShape.currentText() == "":
	    QMessageBox.information(self, "Random Points", "No input layer specified")
	elif self.outShape.text() == "":
	    QMessageBox.information(self, "Random Points", "Please specify output shapefile")
	else:
		inName = self.inShape.currentText()
		self.progressBar.setValue(1)
		outPath = self.outShape.text()
		self.progressBar.setValue(2.5)
		if outPath.contains("\\"):
			outName = outPath.right((outPath.length() - outPath.lastIndexOf("\\")) - 1)
		else:
			outName = outPath.right((outPath.length() - outPath.lastIndexOf("/")) - 1)
		if outName.endsWith(".shp"):
			outName = outName.left(outName.length() - 4)
		self.progressBar.setValue(5)
		mLayer = self.getMapLayerByName(unicode(inName))
		if mLayer.type() == mLayer.VECTOR:
			inLayer = QgsVectorLayer(unicode(mLayer.source(),'latin1'),  unicode(mLayer.name(),'latin1'),  unicode(mLayer.getDataProvider().name()))
			if self.rdoUnstratified.isChecked():
				design = "unstratified"
				value = self.spnUnstratified.value()
			elif self.rdoStratified.isChecked():
				design = "stratified"
				value = self.spnStratified.value()
			elif self.rdoDensity.isChecked():
				design = "density"
				value = self.spnDensity.value()
			else:
				design = "field"
				value = unicode(self.cmbField.currentText())

		if self.chkMinimum.isChecked():
			minimum = self.spnMinimum.value()
		else:
			minimum = 0.00
		self.progressBar.setValue(10)
		self.randomize(inLayer, outPath, minimum, design, value, self.progressBar)
		self.progressBar.setValue(100)
		self.outShape.clear()
		addToTOC = QMessageBox.question(self, "Random Points", "Created output point Shapefile:\n" + outPath 
			+ "\n\nWould you like to add the new layer to the TOC?", QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
		if addToTOC == QMessageBox.Yes:
			self.vlayer = QgsVectorLayer(outPath, unicode(outName), "ogr")
			QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
		self.progressBar.setValue(0)            

    def outFile(self):
		fileDialog = QFileDialog()
		settings = QSettings()
		dirName = settings.value("/UI/lastShapefileDir").toString()
		fileDialog.setDirectory(dirName)
		fileDialog.setDefaultSuffix(QString("shp"))
		fileDialog.setFileMode(QFileDialog.AnyFile)
		encodingBox = QComboBox()
		l = QLabel("Encoding:",fileDialog)
		fileDialog.layout().addWidget(l)
		fileDialog.layout().addWidget(encodingBox)
		encodingBox.addItem("BIG5") 
		encodingBox.addItem("BIG5-HKSCS")
		encodingBox.addItem("EUCJP")
		encodingBox.addItem("EUCKR")
		encodingBox.addItem("GB2312")
		encodingBox.addItem("GBK") 
		encodingBox.addItem("GB18030")
		encodingBox.addItem("JIS7") 
		encodingBox.addItem("SHIFT-JIS")
		encodingBox.addItem("TSCII")
		encodingBox.addItem("UTF-8")
		encodingBox.addItem("UTF-16")
		encodingBox.addItem("KOI8-R")
		encodingBox.addItem("KOI8-U") 
		encodingBox.addItem("ISO8859-1")
		encodingBox.addItem("ISO8859-2")
		encodingBox.addItem("ISO8859-3")
		encodingBox.addItem("ISO8859-4")
		encodingBox.addItem("ISO8859-5")
		encodingBox.addItem("ISO8859-6")
		encodingBox.addItem("ISO8859-7")
		encodingBox.addItem("ISO8859-8") 
		encodingBox.addItem("ISO8859-8-I")
		encodingBox.addItem("ISO8859-9")
		encodingBox.addItem("ISO8859-10")
		encodingBox.addItem("ISO8859-13")
		encodingBox.addItem("ISO8859-14")
		encodingBox.addItem("ISO8859-15")
		encodingBox.addItem("IBM 850")
		encodingBox.addItem("IBM 866")
		encodingBox.addItem("CP874") 
		encodingBox.addItem("CP1250")
		encodingBox.addItem("CP1251")
		encodingBox.addItem("CP1252")
		encodingBox.addItem("CP1253")
		encodingBox.addItem("CP1254")
		encodingBox.addItem("CP1255")
		encodingBox.addItem("CP1256")
		encodingBox.addItem("CP1257") 
		encodingBox.addItem("CP1258") 
		encodingBox.addItem("Apple Roman")
		encodingBox.addItem("TIS-620")
		encodingBox.setItemText(encodingBox.currentIndex(), QString(QTextCodec.codecForLocale().name()))
		filtering = QString("Shapefiles (*.shp)")
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
 		fileDialog.setFilter(filtering)
		fileDialog.setConfirmOverwrite(True)
		if not fileDialog.exec_() == 1:
			return
		self.shapefileName = unicode(fileDialog.selectedFiles().first())
		self.encoding = unicode(encodingBox.currentText())
		self.outShape.clear()
		self.outShape.insert(self.shapefileName)
	
	
# Generate list of random points     
    def simpleRandom(self, n, bound, xmin, xmax, ymin, ymax):
		seed()
		points = []
		i = 1
		while i <= n:
			pGeom = QgsGeometry().fromPoint(QgsPoint(xmin + (xmax-xmin) * random(), ymin + (ymax-ymin) * random()))
			if pGeom.intersects(bound):
				points.append(pGeom)
				i = i + 1
		return points
	
# Get vector layer by name from TOC     
    def getVectorLayerByName(self, myName):
		mc = self.iface.getMapCanvas()
		nLayers = mc.layerCount()
		for l in range(nLayers):
			layer = mc.getZpos(l)
			if layer.name() == unicode(myName):
				vlayer = QgsVectorLayer(unicode(layer.source()),  unicode(myName),  unicode(layer.getDataProvider().name()))
				if vlayer.isValid():
					return vlayer
				else:
					QMessageBox.information(self, "Generate Centroids", "Vector layer is not valid")
	
# Get map layer by name from TOC     
    def getMapLayerByName(self, myName):
    	mc = self.iface.getMapCanvas()
    	nLayers = mc.layerCount()
    	for l in range(nLayers):
    		layer = mc.getZpos(l)
    		if layer.name() == unicode(myName):
    			if layer.isValid():
    				return layer	
# Retreive the field map of a vector Layer
    def getFieldList(self, vlayer):
    	fProvider = vlayer.getDataProvider()
    	feat = QgsFeature()
    	allAttrs = fProvider.allAttributesList()
    	fProvider.select(allAttrs)
    	myFields = fProvider.fields()
    	return myFields
	

    def randomize(self, inLayer, outPath, minimum, design, value, progressBar):
		outFeat = QgsFeature()
		points = self.loopThruPolygons(inLayer, value, design, progressBar)

		fields = { 0 : QgsField("ID", QVariant.Int) }
		check = QFile(self.shapefileName)
		if check.exists():
			if not QgsVectorFileWriter.deleteShapeFile(self.shapefileName):
				return
		writer = QgsVectorFileWriter(self.shapefileName, self.encoding, fields, QGis.WKBPoint, None)
		#writer = QgsVectorFileWriter(unicode(outPath), "CP1250", fields, QGis.WKBPoint, None)
		idVar = 0
		count = 70.00
		add = 30.00 / len(points)
		for i in points:
			outFeat.setGeometry(i)
			outFeat.addAttribute(0, QVariant(idVar))
			writer.addFeature(outFeat)
			idVar = idVar + 1
			count = count + add
			progressBar.setValue(count)
		del writer
	
#   
    def loopThruPolygons(self, inLayer, numRand, design, progressBar):
		sProvider = inLayer.getDataProvider()
		sAllAttrs = sProvider.allAttributesList()
		sProvider.select(sAllAttrs)
		sFeat = QgsFeature()
		sGeom = QgsGeometry()
		sPoints = []
		if design == "field":
			for (i, attr) in sProvider.fields().iteritems():
				if (unicode(numRand) == attr.name()): index = i #get input field index
		count = 10.00
		add = 60.00 / sProvider.featureCount()
		while sProvider.getNextFeature(sFeat):
			sGeom = sFeat.geometry()
			if design == "density":
				sDistArea = QgsDistanceArea()
				value = int(round(numRand * sDistArea.measure(sGeom)))
			elif design == "field":
				sAtMap = sFeat.attributeMap()
				value = sAtMap[index].toInt()[0]
			else:
				value = numRand
			sExt = sGeom.boundingBox()
			sPoints.extend(self.simpleRandom(value, sGeom, sExt.xMin(), sExt.xMax(), sExt.yMin(), sExt.yMax()))
			count = count + add
			progressBar.setValue(count)
		return sPoints
