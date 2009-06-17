from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *
from file_menu.newproject import Geography
from misc.map_toolbar import *
from results_preprocessor import *

# Inputs for this module
resultsloc = "C:/populationsynthesis/gui/results"
resultmap = "bg04_selected.shp"

class Indgeo(Matplot):
    def __init__(self, project, parent=None):
        res = ResultsGen(project)
        del res
        Matplot.__init__(self)
        self.setMinimumSize(QSize(1000,500))
        self.setWindowTitle("Individual Geography Statistics")
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()


        if self.project.resolution == "County":
            self.res_prefix = "co"
        if self.project.resolution == "Tract":
            self.res_prefix = "tr"
        if self.project.resolution == "Blockgroup":
            self.res_prefix = "bg"
        self.stateCode = self.project.stateCode[self.project.state]
        resultfilename = self.res_prefix+self.stateCode+"_selected"
        self.resultsloc = self.project.location + os.path.sep + self.project.name + os.path.sep + "results"
        
        self.resultfileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".shp")

        
        #self.makeComboBox()
        self.makeMapWidget()
        #self.vbox.addWidget(self.geocombobox)
        self.vbox.addWidget(self.mapwidget)
        self.vboxwidget = QWidget()
        self.vboxwidget.setLayout(self.vbox)
        vbox2 = QVBoxLayout()
        self.vboxwidget2 = QWidget()
        self.vboxwidget2.setLayout(vbox2)
        self.labelwidget = QWidget()
        labellayout = QGridLayout(None)
        self.labelwidget.setLayout(labellayout)
        labellayout.addWidget(QLabel("Selected Geography: " ),1,1)
        labellayout.addWidget(QLabel("AARD: " ),2,1)
        labellayout.addWidget(QLabel("P Value: "),3,1)
        self.aardval = QLabel("")
        self.pval = QLabel("")
        self.selgeog = QLabel("")
        self.aardval.setAlignment(Qt.AlignLeft)
        self.pval.setAlignment(Qt.AlignLeft)
        self.selgeog.setAlignment(Qt.AlignLeft)
        labellayout.addWidget(self.selgeog ,1,2)
        labellayout.addWidget(self.aardval,2,2)
        labellayout.addWidget(self.pval,3,2)

        vbox2.addWidget(self.labelwidget)
        vbox2.addWidget(self.canvas)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.vboxwidget)
        self.hbox.addWidget(self.vboxwidget2)

        self.setLayout(self.hbox)
        self.on_draw()
        #self.connect(self.geocombobox, SIGNAL("currentIndexChanged(const QString&)"), self.on_draw)
        self.connect(self.toolbar, SIGNAL("currentGeoChanged"), self.on_draw)
        
        self.selcounty = "0"
        self.seltract = "0"
        self.selblkgroup = "0"
        self.pumano = -1

    def accept(self):
        self.projectDBC.dbc.close()
        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        f = open(self.resultfileloc)
        QDialog.reject(self)


    def on_draw(self, provider=None, selfeat=None ):

        if provider != None:
            blkgroupidx = provider.indexFromFieldName("BLKGROUP")
            tractidx = provider.indexFromFieldName("TRACT")
            countyidx = provider.indexFromFieldName("COUNTY")
            
            attrMap = selfeat.attributeMap()
            try:
                self.selcounty = attrMap[countyidx].toString().trimmed()
            except Exception, e:
                print "Exception: %s" %e
                
            if blkgroupidx == -1 & tractidx == -1:
                self.selgeog.setText("County - " + self.selcounty)
            if tractidx != -1:
                self.seltract = ('%s'%(attrMap[tractidx].toString().trimmed())).ljust(6,'0')
                if blkgroupidx == -1:
                    self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract)
                else:
                    self.selblkgroup = attrMap[blkgroupidx].toString().trimmed()
                    self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract + "; BlockGroup - " + self.selblkgroup)
            
            self.ids = []
            self.act = []
            self.syn = []
            # clear the axes
            self.axes.clear()
            self.axes.grid(True)
            self.axes.set_xlabel("Joint Frequency Distribution from IPF")
            self.axes.set_ylabel("Synthetic Joint Frequency Distribution")
            self.axes.set_xbound(0)
            self.axes.set_ybound(0)


            
            self.retrieveResults()

            provider.fields()
            if len(self.ids) > 0:
                scat_plot = self.axes.scatter(self.act, self.syn)
                scat_plot.axes.set_xbound(0)
                scat_plot.axes.set_ybound(0)
            else:
                pass
            self.canvas.draw()

    def makeComboBox(self):
        self.geocombobox = QComboBox(self)
        self.geocombobox.addItems(["tract: 4002, bg: 1", "tract: 4002, bg: 2"])
        self.geocombobox.setFixedWidth(400)
        self.current = self.geocombobox.currentText()

    def makeMapWidget(self):
        self.mapcanvas = QgsMapCanvas()
        self.mapcanvas.setCanvasColor(QColor(255,255,255))
        self.mapcanvas.enableAntiAliasing(True)
        self.mapcanvas.useQImageToRender(False)
        self.layer = QgsVectorLayer(self.resultfileloc, "Selgeogs", "ogr")
        renderer = self.layer.renderer()
        renderer.setSelectionColor(QColor(255,255,0))
        symbol = renderer.symbols()[0]
        symbol.setFillColor(QColor(153,204,0))
        if not self.layer.isValid():
            return
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.mapcanvas.setExtent(self.layer.extent())
        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        self.mapcanvas.setLayerSet(layers)
        self.toolbar = Toolbar(self.mapcanvas, self.layer)
        self.toolbar.hideDragTool()
        maplayout = QVBoxLayout()
        maplayout.addWidget(self.toolbar)
        maplayout.addWidget(self.mapcanvas)
        self.mapwidget = QWidget()
        self.mapwidget.setLayout(maplayout)

    def getPUMA5(self, geo):
        query = QSqlQuery(self.projectDBC.dbc)
        
        if not geo.puma5:
            if self.project.resolution == 'County':
                geo.puma5 = 0

            elif self.project.resolution == 'Tract':
                if not query.exec_("""select puma5 from geocorr where state = %s and county = %s and tract = %s and bg = 1""" 
                                   %(geo.state, geo.county, geo.tract)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]
            else:
                if not query.exec_("""select puma5 from geocorr where state = %s and county = %s and tract = %s and bg = %s""" 
                                   %(geo.state, geo.county, geo.tract, geo.bg)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]

        return geo


    def retrieveResults(self):
        
        # Get p-values and aard-values from performance statistics
        performancetable = "performance_statistics"
        aardvalvar = "aardvalue"
        pvaluevar = "pvalue"
        vars = aardvalvar + "," + pvaluevar 
        filter = ""
        group = ""

        if self.selcounty <> "0":
            filter_act = "tract=0 and bg=0"
            filter_syn = "county=" + str(self.selcounty) + " and tract=0 and bg=0"

        elif self.seltract <> "0":
            filter_act = "tract=" + str(self.seltract) + " and " + "bg=0"
            filter_syn = "county=" + str(self.selcounty) + " and " +"tract=" + str(self.seltract) + " and " + "bg=0"

        else:
            filter_act = "tract=" + str(self.seltract) + " and " + "bg=" + str(self.selblkgroup)
            filter_syn = "county=" + str(self.selcounty) + " and " +"tract=" + str(self.seltract) + " and " + "bg=" + str(self.selblkgroup)
            


        query = self.executeSelectQuery(self.projectDBC.dbc,vars, performancetable, filter_syn, group)
        aardval = 0.0
        pval = 0.0
        if query:
            while query.next():
                aardval = query.value(0).toDouble()[0]
                pval = query.value(1).toDouble()[0]
                                     
        self.aardval.setText("%.4f" %aardval)
        self.pval.setText("%.4f" %pval)
        
        geo = Geography(self.stateCode, int(self.selcounty), int(self.seltract), int(self.selblkgroup))
        geo = self.getPUMA5(geo)
        
        self.pumano = geo.puma5
        
        # Get and populate the actual and synthetics unique person type frequencies for the scatter plot
        if int(self.pumano) > 0:
            actualtable = "person_" + str(self.pumano) + "_joint_dist"
            vars = "personuniqueid" + "," + "frequency"
            group = "personuniqueid"
            query = self.executeSelectQuery(self.projectDBC.dbc,vars, actualtable, filter_act, group)
            if query:
                while query.next():
                    id= query.value(0).toInt()[0]
                    freq = query.value(1).toDouble()[0]
                    self.ids.append(id)
                    self.act.append(freq)
                
            syntable = "person_synthetic_data"
            vars = "personuniqueid" + "," + "sum(frequency)"
            group = "personuniqueid"
            query = self.executeSelectQuery(self.projectDBC.dbc,vars, syntable, filter_syn, group)
            self.syn = [0.0] * len(self.act)
            if query:
                while query.next():
                    id= query.value(0).toInt()[0]
                    freq = query.value(1).toDouble()[0]
                    if id in self.ids:
                        idx = self.ids.index(id)
                        self.syn[idx] = freq



        
def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

