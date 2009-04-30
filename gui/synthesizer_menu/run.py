import datetime, time, numpy, re, sys
import MySQLdb
import pp


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *

from database.createDBConnection import createDBC
from synthesizer_algorithm.prepare_data import prepare_data
from synthesizer_algorithm.drawing_households import person_index_matrix
from synthesizer_algorithm.demo import configure_and_run
from synthesizer_algorithm.demo_parallel import run_parallel
from gui.file_menu.newproject import Geography
from gui.misc.widgets import VariableSelectionDialog, ListWidget
from gui.misc.errors  import *

import heuristic_algorithm
import psuedo_sparse_matrix
import drawing_households
import adjusting_pums_joint_distribution
import ipf
import scipy
import scipy.stats
import numpy
import MySQLdb
import time
import sys


class RunDialog(QDialog):
    
    def __init__(self, project, parent=None):
        super(RunDialog, self).__init__(parent)
        
        self.setWindowTitle("PopGen: Run Synthesizer")
        self.setWindowIcon(QIcon("../images/run.png"))
        self.setMinimumSize(800,500)

        self.project = project

        self.projectDBC = createDBC(self.project.db, self.project.filename)
        self.projectDBC.dbc.open()

        self.runGeoIds = []
        
        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        selGeographiesLabel = QLabel("Selected Geographies")
        self.selGeographiesList = ListWidget()
        outputLabel = QLabel("Output Window")
        self.outputWindow = QTextEdit()
        selGeographiesButton = QPushButton("Select Geographies")
        self.runSynthesizerButton = QPushButton("Run Synthesizer")
        self.runSynthesizerButton.setEnabled(False)

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(selGeographiesButton)
        vLayout1.addWidget(selGeographiesLabel)
        vLayout1.addWidget(self.selGeographiesList)

        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(self.runSynthesizerButton)
        vLayout2.addWidget(outputLabel)
        vLayout2.addWidget(self.outputWindow)

        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout1)
        hLayout.addLayout(vLayout2)
        
        vLayout3 = QVBoxLayout()
        vLayout3.addLayout(hLayout)
        vLayout3.addWidget(dialogButtonBox)

        
        self.setLayout(vLayout3)
        
        self.connect(selGeographiesButton, SIGNAL("clicked()"), self.selGeographies)
        self.connect(self.runSynthesizerButton, SIGNAL("clicked()"), self.runSynthesizer)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))


    def accept(self):
        self.projectDBC.dbc.close()

        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.accept(self)

    def runSynthesizer(self):
        
        date = datetime.date.today()
        ti = time.localtime()

        self.outputWindow.append("Project Name - %s" %(self.project.name))
        self.outputWindow.append("Population Synthesized at %s:%s:%s on %s" %(ti[3], ti[4], ti[5], date))

        preprocessDataTables = ['sparse_matrix_0', 'index_matrix_0', 'housing_synthetic_data', 'person_synthetic_data',
                                'performance_statistics', 'hhld_0_joint_dist', 'gq_0_joint_dist', 'person_0_joint_dist']

        query = QSqlQuery()
        if not query.exec_("""show tables"""):
            raise FileError, self.query.lastError().text()
        
        projectTables = []
        missingTables = []
        missingTablesString = ""
        while query.next():
            projectTables.append('%s' %(query.value(0).toString()))
            
        for i in preprocessDataTables:
            try:
                projectTables.index(i)
            except:
                missingTablesString = missingTablesString + ', ' + i
                missingTables.append(i)

        if len(missingTables) > 0:
            reply = QMessageBox.warning(self, "PopSim: Run Synthesizer", "The following tables are missing %s, "
                                        " the program will run the prepare data step." %(missingTablesString[:-2]))
            self.prepareData()
        # For now implement it without checking for each individual table that is created in this step
        # in a later implementation check for each table before you proceed with the creation of that particular table

        self.readData()

        if len(self.selectedGeoidsText) > 0:

            for i in self.selectedGeoidsText:
                i = re.split("[,]", i)
                state, county, tract, bg = i


                geo = Geography(state, county, tract, bg)
                
                geo = self.getPUMA5(geo) 


                
                try:
                    self.runGeoIds.index(geo)
                except:
                    self.runGeoIds.append(geo)
                

            reply = QMessageBox.question(self, "PopGen: Run Synthesizer", """Do you wish to run the synthesizer in parallel """
                                          """to take advantage of multiple cores on your processor""", QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                run_parallel(self.project, self.runGeoIds, self.indexMatrix, self.pIndexMatrix)
                pass
            else:
                for geo in self.runGeoIds:
                    self.outputWindow.append("Running Syntheiss for geography State - %s, County - %s, Tract - %s, BG - %s"
                                             %(geo.state, geo.county, geo.tract, geo.bg))
                    configure_and_run(self.project, self.indexMatrix, self.pIndexMatrix, geo)


    def getPUMA5(self, geo):
        query = QSqlQuery()
        
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

    def selGeographies(self):
        geoids = self.allGeographyids()
        dia = VariableSelectionDialog(geoids, title = "PopGen: Select geographies for synthesis", icon = "../images/run.png")
        if dia.exec_():
            self.selectedGeoidsText = []
            
            if dia.selectedVariableListWidget.count() > 0:
                self.selGeographiesList.clear()
                for i in range(dia.selectedVariableListWidget.count()):
                    itemText = dia.selectedVariableListWidget.item(i).text()
                    self.selectedGeoidsText.append(itemText)
                self.selGeographiesList.addItems(self.selectedGeoidsText)
                self.runSynthesizerButton.setEnabled(True)
            else:
                self.selGeographiesList.clear()
                self.runSynthesizerButton.setEnabled(False)
        

    def allGeographyids(self):
        query = QSqlQuery()
        
        for i in self.project.region.keys():
            countyName = i
            stateName = self.project.region[i]
            countyText = '%s,%s' %(countyName, stateName)
            countyCode = self.project.countyCode[countyText]
            stateCode = self.project.stateCode[stateName]
            if self.project.resolution == 'County':
                if not query.exec_("""select state, county from geocorr where state = %s and county = %s"""
                                   """ group by state, county"""
                                   %(stateCode, countyCode)):
                    raise FileError, query.lastError().text()
            elif self.project.resolution == 'Tract':
                if not query.exec_("""select state, county, tract from geocorr where state = %s and county = %s"""
                                   """ group by state, county, tract"""
                                   %(stateCode, countyCode)):
                    raise FileError, query.lastError().text()
            else:
                if not query.exec_("""select state, county, tract, bg from geocorr where state = %s and county = %s"""
                                   """ group by state, county, tract, bg"""
                                   %(stateCode, countyCode)):
                    raise FileError, query.lastError().text()                
        #return a dictionary of all VALID geographies
        
            STATE, COUNTY, TRACT, BG = range(4)
            
            allGeoids = {}
            tract = 0
            bg = 0

            while query.next():
                state = query.value(STATE).toInt()[0]
                county = query.value(COUNTY).toInt()[0]
                
                if self.project.resolution == 'Tract' or self.project.resolution == 'Blockgroup':
                    tract = query.value(TRACT).toInt()[0]
                if self.project.resolution == 'Blockgroup':
                    bg = query.value(BG).toInt()[0]
                
                id = '%s,%s,%s,%s' %(state, county, tract, bg)
                idText = 'State - %s, County - %s, Tract - %s, Block Group - %s' %(state, county, tract, bg)
                
                allGeoids[id] = idText

        return allGeoids

        
    def prepareData(self):
        import MySQLdb
        db = MySQLdb.connect(user = '%s' %self.project.db.username, 
                             passwd = '%s' %self.project.db.password,
                             db = '%s' %self.project.name)
        prepare_data(db)

        db.commit()
        db.close()


    def readData(self):
        db = MySQLdb.connect(user = '%s' %self.project.db.username, 
                             passwd = '%s' %self.project.db.password,
                             db = '%s' %self.project.name)
        dbc = db.cursor()

        #dbc.execute("""select * from sparse_matrix1_%s""" %(0))
        #self.sparseMatrix = numpy.asarray(dbc.fetchall())

        dbc.execute("""select * from index_matrix_%s""" %(0))
        self.indexMatrix = numpy.asarray(dbc.fetchall())
        
        import time
        ti = time.time()

        self.pIndexMatrix = person_index_matrix(db)

        print self.pIndexMatrix[31595, :]

        print 'person Index Matrix processed if - %.4f' %(time.time()-ti)

        dbc.close()
        db.close()



    def checkIfTableExists(self, tablename):
        # 0 - some other error, 1 - overwrite error (table deleted)
        if not self.query.exec_("""create table %s (dummy text)""" %tablename):
            if self.query.lastError().number() == 1050:
                reply = QMessageBox.question(None, "PopSim: Processing Data",
                                             QString("""A table with name %s already exists. Do you wish to overwrite?""" %tablename),
                                             QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not self.query.exec_("""drop table %s""" %tablename):
                        raise FileError, self.query.lastError().text()
                    return 1
                else:
                    return 0
            else:
                raise FileError, self.query.lastError().text()
        else:
            if not self.query.exec_("""drop table %s""" %tablename):
                raise FileError, self.query.lastError().text()
            return 1




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    a = '10'
    dia = RunDialog(a)
    dia.show()
    
    app.exec_()
