from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from coreplot import *

class Hhdist(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.hhldvariables = self.project.selVariableDicts.hhld.keys()
        self.gqvariables = self.project.selVariableDicts.gq.keys()
        self.hhldvariables.sort()
        self.gqvariables.sort()
        
        self.setWindowTitle("Housing Attributes Distribution")
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
        hhldvarstr = ""
        gqvarstr = ""
        for i in self.hhldvariables:
            hhldvarstr = hhldvarstr + i + ','
        hhldvarstr = hhldvarstr[:-1]
        for i in self.gqvariables:
            gqvarstr = gqvarstr + i + ','
        gqvarstr = gqvarstr[:-1]
        
        query = QSqlQuery(self.projectDBC.dbc)
        query.exec_(""" DROP TABLE IF EXISTS temphhld""")
        if not query.exec_("""CREATE TABLE temphhld SELECT housing_synthetic_data.*,%s FROM housing_synthetic_data"""
            """ LEFT JOIN hhld_sample using (serialno)""" %(hhldvarstr)):
            raise FileError, query.lastError().text()    
        query.exec_(""" DROP TABLE IF EXISTS tempgq""")            
        if not query.exec_("""CREATE TABLE tempgq SELECT housing_synthetic_data.*,%s FROM housing_synthetic_data"""
            """ LEFT JOIN gq_sample using (serialno)""" %(gqvarstr)):
            raise FileError, query.lastError().text()   
            
    def on_draw(self):
        """ Redraws the figure
        """
        self.current = self.hhcombobox.currentText()
        if self.current in self.hhldvariables:
            self.categories = self.project.selVariableDicts.hhld[self.current].keys()
            self.corrControlVariables =  self.project.selVariableDicts.hhld[self.current].values()
            tableAct = "hhld_marginals"
            tableEst = "temphhld"
            seldict = self.project.selVariableDicts.hhld
        else:
            self.categories = self.project.selVariableDicts.gq[self.current].keys()
            self.corrControlVariables =  self.project.selVariableDicts.gq[self.current].values()
            tableAct = "gq_marginals"
            tableEst = "tempgq"
            seldict = self.project.selVariableDicts.gq
        self.categories.sort()

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
        
        for i in self.categories:
            variable = seldict[self.current][i]
            self.catlabels.append(variable)
            variableAct = "sum(%s)" %variable
            queryAct = self.executeSelectQuery(variableAct, tableAct, filterAct)
            while queryAct.next():
                value = queryAct.value(0).toInt()[0]
                actTotal.append(value)

            category = "%s" %i
            category = category.split()[-1]
            filterEst = self.current + " = %s" % category
            variableEst = "sum(frequency)"
            queryEst = self.executeSelectQuery(variableEst, tableEst, filterEst)
            
            while queryEst.next():
                value = queryEst.value(0).toInt()[0]
                estTotal.append(value)        
            
        # clear the axes and redraw the plot anew
        self.axes.clear()        
        self.axes.grid(True)
        N=len(actTotal)
        ind = np.arange(N)
        width = 0.35
        
        rects1 = self.axes.bar(ind, actTotal, width, color='r')
        rects2 = self.axes.bar(ind+width, estTotal, width, color='y')
        self.axes.set_xlabel("Housing Attributes")
        self.axes.set_ylabel("Frequencies")
        self.axes.set_xticks(ind+width)
        self.axes.set_xticklabels(self.catlabels)
        self.axes.legend((rects1[0], rects2[0]), ('Actual', 'Synthetic'))
        self.canvas.draw() 
        
    def makeComboBox(self):
        self.hhcombobox = QComboBox(self)
        self.hhcombobox.addItems(self.hhldvariables+self.gqvariables)
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

