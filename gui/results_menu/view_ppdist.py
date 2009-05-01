from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from coreplot import *

# Inputs for this module
ppdist_location = "C:/populationsynthesis/gui/results/hhdist_test.txt"

class Ppdist(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)

        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.variables = self.project.selVariables.person.keys()
        self.dimensions = [len(project.selVariables.hhld[i].keys()) for i in self.variables]


        self.setWindowTitle("Person Attributes Distribution")
        self.makeComboBox()
        self.vbox.addWidget(self.hhcombobox)
        self.vbox.addWidget(self.canvas)
        self.setLayout(self.vbox)


        self.on_draw()
        self.connect(self.hhcombobox, SIGNAL("currentIndexChanged(const QString&)"), self.on_draw)


    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)


    def on_draw(self):
        """ Redraws the figure
        """
        self.current = self.hhcombobox.currentText()      
        self.categories = self.project.selVariables.person[self.current].keys()
        self.corrControlVariables =  self.project.selVariables.person[self.current].values()


        print self.project.region.keys()
        
        filterAct = ""

        self.countyCodes = []
        for i in self.project.region.keys():
            code = self.project.countyCode['%s,%s' % (i, self.project.state)]
            self.countyCodes.append(code)
            filterAct = filterAct + "county = %s or " %code

        filterAct = filterAct[:-3]
        print filterAct


        actTotal = []
        estTotal = []
        for i in self.categories:
            
            tableAct = "person_marginals"
            variable = self.project.selVariables.person[self.current][i]
            variableAct = "sum(%s)" %variable
            queryAct = self.executeSelectQuery(variableAct, tableAct, filterAct)

            while queryAct.next():
                value = queryAct.value(0).toInt()[0]
                actTotal.append(value)

            category = "%s" %i

            category = category.split()[-1]

            tableEst = "person_synthetic_data"
            filterEst = self.current + " = %s" % category
            
            variableEst = "sum(frequency)"
            queryEst = self.executeSelectQuery(variableEst, tableEst, filterEst)

            while queryEst.nexT():
                value = queryEst.value(0).toInt()[0]
                estTotal.append(value)

        print actTotal
        print estTotal


        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        N=len(actTotal)
        ind = np.arange(N)
        width = 0.35
        
        rects1 = self.axes.bar(ind, actTotal, width, color='r')
        rects2 = self.axes.bar(ind+width, estTotal, width, color='y')
        self.axes.set_xlabel("Person Attributes")
        self.axes.set_ylabel("Frequencies")
        self.axes.set_xticks(ind+width)
        # generic labels should be created
        self.axes.set_xticklabels(self.categories)
        self.axes.legend((rects1[0], rects2[0]), ('Actual', 'Synthetic'))

        self.canvas.draw()        



        
    def makeComboBox(self):
        self.hhcombobox = QComboBox(self)
        self.hhcombobox.addItems(self.variables)
        self.hhcombobox.setFixedWidth(400)



def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

