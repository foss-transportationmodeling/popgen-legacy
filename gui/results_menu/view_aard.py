from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *

# Inputs for this module
aard_location = "C:/populationsynthesis/gui/results/aard_test.txt"

class Absreldiff(Matplot):
    def __init__(self, parent=None):
        Matplot.__init__(self)
        self.setWindowTitle("Average Absolute Relative Difference Distribution")
        self.vbox.addWidget(self.canvas)
        self.setLayout(self.vbox)
        self.on_draw()

    def on_draw(self):
        """ Redraws the figure
        """
        f = open(aard_location)
        err = []
        for line in f:
            vals = (line.split('\n'))[0].split(',')
            err.append(float(vals[2]))
            
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        
        #self.axes.hist(err, range=(1,10), normed=True, cumulative=False, histtype='bar', align='mid', orientation='vertical', log=False)
        self.axes.hist(err, normed=True, align='mid')
        self.axes.set_xlabel("Average Absolute Relative Differences")
        self.axes.set_ylabel("Proportions")
        self.canvas.draw()        


def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

