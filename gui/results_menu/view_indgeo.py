from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *
from misc.map_toolbar import *

# Inputs for this module
indgeo_location = "C:/populationsynthesis/gui/results/indgeo_test.txt"
resultsloc = "C:/populationsynthesis/gui/results"
resultmap = "bg04_selected.shp"

class Indgeo(Matplot):
    def __init__(self, parent=None):
        Matplot.__init__(self)
        self.setWindowTitle("Individual Geography Statistics")
        self.setFixedSize(QSize(1000,500))
        
        self.makeComboBox()
        self.makeMapWidget()
        self.vbox.addWidget(self.geocombobox)
        self.vbox.addWidget(self.mapwidget)
        self.vboxwidget = QWidget()
        self.vboxwidget.setLayout(self.vbox)
        vbox2 = QVBoxLayout()
        self.vboxwidget2 = QWidget()
        self.vboxwidget2.setLayout(vbox2)
        vbox2.addWidget(QLabel("AARD:" + "some aard value"))
        vbox2.addWidget(QLabel("P Value:" + "some p-values"))
        vbox2.addWidget(self.canvas)
        
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.vboxwidget)
        self.hbox.addWidget(self.vboxwidget2)
        
        self.setLayout(self.hbox)
        self.on_draw()
        self.connect(self.geocombobox, SIGNAL("currentIndexChanged(const QString&)"), self.on_draw)

    def on_draw(self):
        """ Redraws the figure
        """
        self.current = self.geocombobox.currentText()
        print "drawing again " + self.current
        f = open(indgeo_location)
        act = []
        syn = []
        for line in f:
            vals = (line.split('\n'))[0].split(',')
            act.append(float(vals[1]))
            syn.append(float(vals[2]))
            
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        
        self.axes.scatter(act, syn)
        self.axes.set_xlabel("Joint Frequency Distribution from IPF")
        self.axes.set_ylabel("Synthetic Joint Frequency Distribution")
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
        layerPath = resultsloc+os.path.sep+resultmap
        self.layer = QgsVectorLayer(layerPath, "Selgeogs", "ogr")        
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
        
def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

