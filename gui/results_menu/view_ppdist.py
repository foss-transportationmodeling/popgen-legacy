from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from coreplot import *

class Ppdist(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.variables = self.project.selVariableDicts.person.keys()
        self.variables.sort()
        self.dimensions = [len(project.selVariableDicts.hhld[i].keys()) for i in self.variables]

        self.setWindowTitle("Person Attributes Distribution")
        self.makeComboBox()
        self.vbox.addWidget(self.hhcombobox)
        self.vbox.addWidget(self.canvas)
        self.setLayout(self.vbox)
        
        self.makeTempTables()
        self.on_draw()
        self.connect(self.hhcombobox, SIGNAL("currentIndexChanged(const QString&)"), self.on_draw)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)

    def makeTempTables(self):
        varstr = ""
        for i in self.variables:
            varstr = varstr + i + ','
        varstr = varstr[:-1]
            
        query = QSqlQuery(self.projectDBC.dbc)
        query.exec_(""" DROP TABLE IF EXISTS temp""")
        if not query.exec_("""CREATE TABLE temp SELECT person_synthetic_data.*,%s FROM person_synthetic_data"""
            """ LEFT JOIN person_sample using (serialno,pnum)""" %(varstr)):
            raise FileError, query.lastError().text()
    
    def on_draw(self):
        """ Redraws the figure  
        """
        self.current = self.hhcombobox.currentText()      
        self.categories = self.project.selVariableDicts.person[self.current].keys()
        self.categories.sort()
        self.corrControlVariables =  self.project.selVariableDicts.person[self.current].values()
        
        filterAct = ""
        self.countyCodes = []
        for i in self.project.region.keys():
            code = self.project.countyCode['%s,%s' % (i, self.project.state)]
            self.countyCodes.append(code)
            filterAct = filterAct + "county = %s or " %code
            
        filterAct = filterAct[:-3]
        
        actTotal = []
        estTotal = []
        self.catlabels = []
        tableAct = "person_marginals"
        for i in self.categories:
            variable = self.project.selVariableDicts.person[self.current][i]
            self.catlabels.append(variable)
            variableAct = "sum(%s)" %variable
            queryAct = self.executeSelectQuery(variableAct, tableAct, filterAct)
            while queryAct.next():
                value = queryAct.value(0).toInt()[0]
                actTotal.append(value)

            category = "%s" %i
            category = category.split()[-1]
            tableEst = "temp"
            filterEst = self.current + " = %s" % category
            variableEst = "sum(frequency)"
            queryEst = self.executeSelectQuery(variableEst, tableEst, filterEst)
            
            while queryEst.next():
                value = queryEst.value(0).toInt()[0]
                estTotal.append(value)
                
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        self.canvas.draw()  
        
        N=len(actTotal)
        ind = np.arange(N)
        width = 0.35
        
        rects1 = self.axes.bar(ind, actTotal, width, color='r')
        rects2 = self.axes.bar(ind+width, estTotal, width, color='y')
        self.axes.set_xlabel("Person Attributes")
        self.axes.set_ylabel("Frequencies")
        self.axes.set_xticks(ind+width)
        # generic labels should be created
        self.axes.set_xticklabels(self.catlabels)
        self.axes.legend((rects1[0], rects2[0]), ('Actual', 'Synthetic'))
        
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

