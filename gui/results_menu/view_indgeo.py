from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *

# Inputs for this module
indgeo_location = "C:/populationsynthesis/gui/results/indgeo_test.txt"

class Indgeo(Matplot):
    def __init__(self, parent=None):
        Matplot.__init__(self)
        self.setWindowTitle("Individual Geography Statistics")
        self.makeComboBox()
        self.vbox.addWidget(self.geocombobox)
        self.vbox.addWidget(self.canvas)
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


def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

