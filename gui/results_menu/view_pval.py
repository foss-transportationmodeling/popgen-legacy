from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *

class Pval(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.project = project
        self.setWindowTitle("P Value Distribution")
        self.vbox.addWidget(self.canvas)
        self.setLayout(self.vbox)
        self.on_draw()


    def on_draw(self):
        """ Redraws the figure
        """
        self.err = []
        self.retrieveResults()
        
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        
        #self.axes.hist(err, range=(1,10), normed=True, cumulative=False, histtype='bar', align='mid', orientation='vertical', log=False)
        self.axes.hist(self.err, normed=False, align='mid')
        self.axes.set_xlabel("P Values")
        self.axes.set_ylabel("Frequency")
        self.canvas.draw()      

    def retrieveResults(self):
        projectDBC = createDBC(self.project.db, self.project.name)
        projectDBC.dbc.open()
        
        # Get p-values from performance statistics
        performancetable = "performance_statistics"
        pvaluevar = "pvalue"
        filter = ""
        group = ""
        query = self.executeSelectQuery(pvaluevar, performancetable, filter, group)
        
        while query.next():
            pval = query.value(0).toDouble()[0]
            self.err.append(pval)
        
        projectDBC.dbc.close()
def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()
