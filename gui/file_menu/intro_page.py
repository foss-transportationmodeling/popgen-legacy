from PyQt4.QtCore import *
from PyQt4.QtGui import *
from misc.widgets import *
from qgis.core import *
from qgis.gui import *
from misc.map_toolbar import *
import countydata


class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super(IntroPage, self).__init__(parent)

        self.nameDummy = True
        self.locationDummy = True
        self.regionDummy = False

        self.setTitle("Step 1: Region")

        # Project Description
        nameLabel = QLabel("Project Name")
        self.nameLineEdit = LineEdit()
        self.nameLineEdit.setText("enter_project_name")
        self.nameLineEdit.selectAll()
        nameLabel.setBuddy(self.nameLineEdit)
        locationLabel = QLabel("Project Location")
        self.locationComboBox = ComboBoxFolder()
        #self.locationComboBox.addItems([QString("C:/"), QString("Browse to select folder...")])
        self.locationComboBox.addItems([QString("C:/SynTest"), QString("Browse to select folder...")])
        locationLabel.setBuddy(self.locationComboBox)
        descLabel = QLabel("Project Description")
        self.descTextEdit = QTextEdit()
        descLabel.setBuddy(self.descTextEdit)

        # Project Description Layout
        projectVLayout = QVBoxLayout()
        projectVLayout.addWidget(nameLabel)
        projectVLayout.addWidget(self.nameLineEdit)
        projectVLayout.addWidget(locationLabel)
        projectVLayout.addWidget(self.locationComboBox)
        projectVLayout.addWidget(descLabel)
        projectVLayout.addWidget(self.descTextEdit)

        # Selecting Counties using the tree widget
        self.countySelectTree = QTreeWidget()
        self.countySelectTree.setColumnCount(1)
        self.countySelectTree.setHeaderLabels(["State/County"])
        self.countySelectTree.setItemsExpandable(True)
        state = QTreeWidgetItem(self.countySelectTree, [QString("State")])
        county = QTreeWidgetItem(state, [QString("County")])
        state = QTreeWidgetItem(self.countySelectTree, [QString("State1")])
        county = QTreeWidgetItem(state, [QString("County1")])

        # Displaying counties and selecting counties using the map
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(255,255,255))
        self.canvas.enableAntiAliasing(True)
        self.canvas.useQImageToRender(False)
        layerPath = "./data/county.shp"
        layerName = "USCounties"
        layerProvider = "ogr"
        self.layer = QgsVectorLayer(layerPath, layerName, layerProvider)

        renderer = self.layer.renderer()
        renderer.setSelectionColor(QColor(255,255,0))
        
        symbol = renderer.symbols()[0]
        symbol.setFillColor(QColor(153,204,0))

 
        if not self.layer.isValid():
            return
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.canvas.setExtent(self.layer.extent())
        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        self.canvas.setLayerSet(layers)


        # Vertical layout of project description elements
        vLayout1 = QVBoxLayout()
        vLayout1.addLayout(projectVLayout)
        vLayout1.addWidget(self.countySelectTree)
        # Vertical layout of map elements
        vLayout2 = QVBoxLayout()
        self.toolbar = Toolbar(self.canvas, self.layer)
        vLayout2.addWidget(self.toolbar)
        vLayout2.addWidget(self.canvas)        
        # Horizontal layout of all elements
        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout1)
        hLayout.addLayout(vLayout2)
        self.setLayout(hLayout)

        self.counties = countydata.CountyContainer(QString("./data/counties.csv"))
        self.populateCountySelectTree()

        self.connect(self.locationComboBox, SIGNAL("activated(int)"), self.locationComboBox.browseFolder)
        self.connect(self.nameLineEdit, SIGNAL("textEdited(const QString&)"), self.nameCheck)
        self.connect(self.locationComboBox, SIGNAL("currentIndexChanged(int)"), self.locationCheck)
        self.connect(self.countySelectTree, SIGNAL("itemSelectionChanged()"), self.regionCheck)


    def nameCheck(self, text):
        self.nameDummy = self.nameLineEdit.check(text)
        self.emit(SIGNAL("completeChanged()"))

    def locationCheck(self, int):
        if self.locationComboBox.currentText() == '':
            self.locationDummy = False
        else:
            self.locationDummy = True
        self.emit(SIGNAL("completeChanged()"))
        
    def regionCheck(self):
        self.selectedCounties = {}
        items = self.countySelectTree.selectedItems()
        if items is not None:

            parent = None
            for i in range(len(items)):
                selection = items[i]
                if selection.parent() is None:
                    selection.setSelected(False)
                    self.regionDummy = False
                else:
                    if parent <> selection.parent():
                        parent = selection.parent()
                        for j in range(i):
                            items[j].setSelected(False)
                    self.regionDummy = True
        else:
            self.regionDummy = False
        self.emit(SIGNAL("completeChanged()"))
        
        for i in self.countySelectTree.selectedItems():
            self.selectedCounties[i.text(0)] = i.parent().text(0)

        self.highlightSelectedCounties()
        
    def highlightSelectedCounties(self):
        self.layer.removeSelection()
        selectedFeatureIds = []
        provider = self.layer.getDataProvider()
        allAttrs = provider.allAttributesList()
        stidx = provider.indexFromFieldName("statename")
        ctyidx = provider.indexFromFieldName("countyname")
        provider.select(allAttrs,QgsRect())
        feat = QgsFeature()
        while provider.getNextFeature(feat):
            attrMap = feat.attributeMap()
            featstate = attrMap[stidx].toString().trimmed()
            featcounty = attrMap[ctyidx].toString().trimmed()
            for county in self.selectedCounties.keys():
                state = self.selectedCounties[county]

                if (featstate.compare(state) == 0 and featcounty.compare(county) == 0):
                    selid = feat.featureId()
                    selectedFeatureIds.append(selid)
                    
        if len(selectedFeatureIds) > 0:
            self.layer.setSelectedFeatures(selectedFeatureIds)
        boundingBox = self.layer.boundingBoxOfSelected()
        boundingBox.scale(4)
        self.canvas.setExtent(boundingBox)
        self.canvas.refresh()

    def populateCountySelectTree(self):
        self.initialLoad()
        self.countySelectTree.clear()
        self.countySelectTree.setColumnCount(1)
        self.countySelectTree.setHeaderLabels(["State/County"])
        self.countySelectTree.setSelectionMode(QAbstractItemView.ExtendedSelection)


        parentFromState = {}
        parentFromStateCounty = {}
        for county in self.counties:
            ancestor = parentFromState.get(county.stateName)
            if ancestor is None:
                ancestor = QTreeWidgetItem(self.countySelectTree, [QString(county.stateName)])
                parentFromState[county.stateName]=ancestor

            stateCounty = "%s%s%s" %(county.stateName, "/", county.countyName)
            parent = parentFromStateCounty.get(stateCounty)
            if parent is None:
                parent = QTreeWidgetItem(ancestor, [QString(county.countyName)])
                parentFromStateCounty[stateCounty] = parent

        self.countySelectTree.sortItems(0, Qt.AscendingOrder)


    

    def initialLoad(self):
        try:
            self.counties.load()
        except IOError, e:
            QMessageBox.warning(self, "Counties - Error", "Failed to load: %s" %e)

    def isComplete(self):
        validate = self.nameDummy and self.locationDummy and self.regionDummy
        if validate:
            return True
        else:
            return False

