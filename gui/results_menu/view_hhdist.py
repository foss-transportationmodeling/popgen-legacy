from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from coreplot import *

# Inputs for this module
hhdist_location = "C:/populationsynthesis/gui/results/hhdist_test.txt"

class Hhdist(Matplot):
    def __init__(self, parent=None):
        Matplot.__init__(self)
        self.setWindowTitle("Housing Attributes Distribution")
        self.makeComboBox()
        self.vbox.addWidget(self.hhcombobox)
        self.vbox.addWidget(self.canvas)
        self.on_draw()
        self.connect(self.hhcombobox, SIGNAL("currentIndexChanged(const QString&)"), self.on_draw)


    def on_draw(self):
        """ Redraws the figure
        """
        f = open(hhdist_location)
        act = []
        syn = []
        for line in f:
            vals = (line.split('\n'))[0].split(',')
            act.append(float(vals[1]))
            syn.append(float(vals[2]))
            
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        N=len(act)
        ind = np.arange(N)
        width = 0.35
        
        rects1 = self.axes.bar(ind, act, width, color='r')
        rects2 = self.axes.bar(ind+width, syn, width, color='y')
        self.axes.set_xlabel("Household Attributes")
        self.axes.set_ylabel("Frequencies")
        self.axes.set_xticks(ind+width)
        self.axes.set_xticklabels(('2 persons', '3 persons'))
        self.axes.legend((rects1[0], rects2[0]), ('Actual', 'Synthetic'))
        
        self.canvas.draw()        
        
    def makeComboBox(self):
        self.hhcombobox = QComboBox(self)
        self.hhcombobox.addItems(["HHSize", "HHType"])
        self.hhcombobox.setFixedWidth(400)
        self.current = self.hhcombobox.currentText()

def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

