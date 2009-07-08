# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from coreplot import *

class Hhdist(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.setFixedSize(800,600)
        self.project = project
        self.valid = False
        if self.isValid():
            self.valid = True
            self.projectDBC = createDBC(self.project.db, self.project.name)
            self.projectDBC.dbc.open()
            self.hhldvariables = self.project.selVariableDicts.hhld.keys()
            self.gqvariables = self.project.selVariableDicts.gq.keys()
            self.hhldvariables.sort()
            self.gqvariables.sort()

            self.setWindowTitle("Distribution of Housing Variables")
            self.setWindowIcon(QIcon("./images/region.png"))
            hhdistWarning = QLabel("""<font color = blue>Note: The above chart compares the actual marginal distributions with """
                                   """ marginal distributions from the synthetic population for the household/"""
                                   """groupquarter variables of interest. </font>""")
            hhdistWarning.setWordWrap(True)
            self.enableindgeo = True
            self.makeComboBox()
            self.vbox.addWidget(self.comboboxholder)
            self.vbox.addWidget(self.canvas)
            self.vbox.addWidget(hhdistWarning)
            self.vbox.addWidget(self.dialogButtonBox)
            self.setLayout(self.vbox)
            self.makeTempTables()
            self.connect(self.attrbox, SIGNAL("currSelChanged"), self.on_draw)
            self.connect(self.geobox, SIGNAL("currSelChanged"), self.on_draw)
        else:
            QMessageBox.warning(self, "Results", "A table with name - housing_synthetic_data does not exist.", QMessageBox.Ok)

    def isValid(self):
        return self.checkIfTableExists("housing_synthetic_data")

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
        self.on_draw()

    def on_draw(self):
        """ Redraws the figure
        """
        self.current = '%s' %self.attrbox.getCurrentText()
        selgeog = '%s' %self.geobox.getCurrentText()
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

        if selgeog == 'All':
            table = "housing_synthetic_data"
            variable = "county,tract,bg"
            queryAct = self.executeSelectQuery(self.projectDBC.dbc,variable, table, "",variable)
            i=0
            if queryAct:
                while queryAct.next():
                    filstr = self.getGeogFilStr(queryAct.value(0).toInt()[0],queryAct.value(1).toInt()[0],queryAct.value(2).toInt()[0])
                    if i == 0:
                        filterAct = "(" + filterAct + filstr + ")"
                        i = 1
                    else:
                        filterAct = filterAct + " or " + "(" + filstr + ")"
        else:
            geosplit = selgeog.split(',')
            filterAct = "county=%s and tract=%s and bg=%s" %(geosplit[1],geosplit[2],geosplit[3])

        actTotal = []
        estTotal = []
        self.catlabels = []

        for i in self.categories:
            variable = seldict[self.current][i]
            self.catlabels.append(variable)
            variableAct = "sum(%s)" %variable
            queryAct = self.executeSelectQuery(self.projectDBC.dbc,variableAct, tableAct, filterAct)
            if queryAct:
                while queryAct.next():
                    value = queryAct.value(0).toInt()[0]
                    actTotal.append(value)
            else:
                break

            category = "%s" %i
            category = category.split()[-1]
            filterEst = self.current + " = %s" % category
            if selgeog != 'All':
                filterEst = filterEst + ' and ' + filterAct
            variableEst = "sum(frequency)"
            queryEst = self.executeSelectQuery(self.projectDBC.dbc,variableEst, tableEst, filterEst)


            if queryEst:
                iteration = 0
                while queryEst.next():
                    value = queryEst.value(0).toInt()[0]
                    estTotal.append(value)
                    iteration = 1
                if iteration == 0:
                    estTotal.append(0)

        # clear the axes and redraw the plot anew
        self.axes.clear()
        self.axes.grid(True)
        N=len(actTotal)
        ind = np.arange(N)
        width = 0.35

        rects1 = self.axes.bar(ind, actTotal, width, color='r')
        rects2 = self.axes.bar(ind+width, estTotal, width, color='y')
        self.axes.set_xlabel("Housing Variables")
        self.axes.set_ylabel("Frequency")
        self.axes.set_xticks(ind+width)
        self.axes.set_xticklabels(self.catlabels)
        self.axes.legend((rects1[0], rects2[0]), ('Actual', 'Synthetic'))
        self.canvas.draw()

    def makeComboBox(self):
        self.comboboxholder = QWidget(self)
        self.hbox = QHBoxLayout()
        self.comboboxholder.setLayout(self.hbox)
        self.attrbox = LabComboBox("Variable:",self.hhldvariables+self.gqvariables)
        self.getGeographies()
        self.geolist.sort()
        self.geobox = LabComboBox("Geography:",["All"] + self.geolist)
        self.hbox.addWidget(self.attrbox)
        if self.enableindgeo:
            self.hbox.addWidget(self.geobox)
        self.hbox.addWidget(QWidget())
        self.hbox.addWidget(QWidget())

    def getGeogFilStr(self,county,tract,bg):
        if self.project.resolution == "County":
            str = "county=%s" %(county)
        if self.project.resolution == "Tract":
            str = "county=%s and tract=%s" %(county,tract)
        if self.project.resolution == "Blockgroup" or self.project.resolution == "TAZ" :
            str = "county=%s and tract=%s and bg=%s" %(county,tract,bg)
        return str


def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

