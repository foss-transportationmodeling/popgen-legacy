# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import datetime, time, numpy, re, sys
import MySQLdb
import pp
import cPickle as pickle

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *

from database.createDBConnection import createDBC
from synthesizer_algorithm.prepare_data import prepare_data
from synthesizer_algorithm.prepare_data_noper import prepare_data_noper
from synthesizer_algorithm.prepare_data_nogqs import prepare_data_nogqs
from synthesizer_algorithm.prepare_data_nogqs_noper import prepare_data_nogqs_noper
from synthesizer_algorithm.drawing_households import person_index_matrix
import synthesizer_algorithm.demo as demo
import synthesizer_algorithm.demo_nogqs as demo_nogqs
import synthesizer_algorithm.demo_noper as demo_noper
import synthesizer_algorithm.demo_nogqs_noper as demo_nogqs_noper

import synthesizer_algorithm.demo_parallel as demo_parallel
import synthesizer_algorithm.demo_parallel_nogqs as demo_parallel_nogqs
import synthesizer_algorithm.demo_parallel_noper as demo_parallel_noper
import synthesizer_algorithm.demo_parallel_nogqs_noper as demo_parallel_nogqs_noper


import synthesizer_algorithm.demo_parallel as demo_parallel
import synthesizer_algorithm.demo_parallel_nogqs as demo_parallel_nogqs
from gui.file_menu.newproject import Geography
from gui.misc.widgets import VariableSelectionDialog, ListWidget
from gui.misc.errors  import *

class RunDialog(QDialog):

    def __init__(self, project, jobserver, parent=None):

        self.job_server = jobserver
        super(RunDialog, self).__init__(parent)

        self.setWindowTitle("Run Synthesizer")
        self.setWindowIcon(QIcon("./images/run.png"))
        self.setMinimumSize(800,500)

        self.project = project

        scenarioDatabase = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.gqAnalyzed = self.isGqAnalyzed()

        self.runGeoIds = []

        self.dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)



        selGeographiesLabel = QLabel("Selected Geographies")
        self.selGeographiesList = ListWidget()
        outputLabel = QLabel("Output Window")
        self.outputWindow = QTextEdit()
        self.selGeographiesButton = QPushButton("Select Geographies")
        self.runSynthesizerButton = QPushButton("Run Synthesizer")
        self.runSynthesizerButton.setEnabled(False)

        runWarning = QLabel("""<font color = blue>Note: Select geographies by clicking on the <b>Select Geographies</b> button """
                            """and then click on <b>Run Synthesizer</b> to start synthesizing population.</font>""")
        runWarning.setWordWrap(True)

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(self.selGeographiesButton)
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
        vLayout3.addWidget(runWarning)
        vLayout3.addWidget(self.dialogButtonBox)


        self.setLayout(vLayout3)

        self.connect(self.selGeographiesButton, SIGNAL("clicked()"), self.selGeographies)
        self.connect(self.runSynthesizerButton, SIGNAL("clicked()"), self.runSynthesizer)
        self.connect(self.dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))


    def accept(self):
        self.projectDBC.dbc.close()

        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.accept(self)


    def variableControlCorrDict(self, vardict):
        varCorrDict = {}
        vars = vardict.keys()
        for i in vars:
            for j in vardict[i].keys():
                cat = (('%s' %j).split())[-1]
                varCorrDict['%s%s' %(i, cat)] = '%s' %vardict[i][j]
        return varCorrDict

    def runSynthesizer(self):

        date = datetime.date.today()
        ti = time.localtime()

        self.outputWindow.append("Project Name - %s" %(self.project.name))
        self.outputWindow.append("Population Synthesized at %s:%s:%s on %s" %(ti[3], ti[4], ti[5], date))

        if self.gqAnalyzed and self.project.selVariableDicts.persControl:
            preprocessDataTables = ['sparse_matrix_0', 'index_matrix_0', 'housing_synthetic_data', 'person_synthetic_data',
                                    'performance_statistics', 'hhld_0_joint_dist', 'gq_0_joint_dist', 'person_0_joint_dist']
        if self.gqAnalyzed and not self.project.selVariableDicts.persControl:
            preprocessDataTables = ['sparse_matrix_0', 'index_matrix_0', 'housing_synthetic_data', 'person_synthetic_data',
                                    'performance_statistics', 'hhld_0_joint_dist', 'gq_0_joint_dist']
        if not self.gqAnalyzed and self.project.selVariableDicts.persControl:
            preprocessDataTables = ['sparse_matrix_0', 'index_matrix_0', 'housing_synthetic_data', 'person_synthetic_data',
                                    'performance_statistics', 'hhld_0_joint_dist', 'person_0_joint_dist']            
        if not self.gqAnalyzed and not self.project.selVariableDicts.persControl:
            preprocessDataTables = ['sparse_matrix_0', 'index_matrix_0', 'housing_synthetic_data', 'person_synthetic_data',
                                    'performance_statistics', 'hhld_0_joint_dist']            

        databaseName = self.project.name + 'scenario' + str(self.project.scenario)
        self.projectDBC.dbc.setDatabaseName(databaseName)
        self.projectDBC.dbc.open()
        
        query = QSqlQuery(self.projectDBC.dbc)
        if not query.exec_("""show tables"""):
            raise FileError, self.query.lastError().text()

        
        varCorrDict = {}
        varCorrDict.update(self.variableControlCorrDict(self.project.selVariableDicts.hhld))
        if self.gqAnalyzed:
            varCorrDict.update(self.variableControlCorrDict(self.project.selVariableDicts.gq))
        varCorrDict.update(self.variableControlCorrDict(self.project.selVariableDicts.person))


        controlAdjDict = {}
        controlAdjDict.update(self.project.adjControlsDicts.hhld)
        if self.gqAnalyzed:
            controlAdjDict.update(self.project.adjControlsDicts.gq)
        if self.project.selVariableDicts.persControl:
            controlAdjDict.update(self.project.adjControlsDicts.person)

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

        self.projectDBC.dbc.setDatabaseName(self.project.name)
        self.projectDBC.dbc.open()

        if len(missingTables) > 0:
            QMessageBox.warning(self, "Prepare Data", "The program will now prepare the data for population synthesis." )
            self.prepareData()
        # For now implement it without checking for each individual table that is created in this step
        # in a later implementation check for each table before you proceed with the creation of that particular table
        else:
            reply = QMessageBox.warning(self, "Prepare Data", """Would you like to prepare the data? """
                                        """Run this step if the control variables or their categories have changed.""",
                                        QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.prepareData()

        self.readData()

        if len(self.runGeoIds) > 0:

            reply = QMessageBox.question(self, "Run Synthesizer", """Would you like to run the synthesizer in parallel """
                                          """to take advantage of multiple cores on your processor?""", QMessageBox.Yes| QMessageBox.No| QMessageBox.Cancel)

            scenarioDatabase = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)
            for i in self.runGeoIds:
                ti = time.time()
                if not query.exec_("""delete from %s.housing_synthetic_data where state = %s and county = %s """
                                   """ and tract = %s and bg = %s  """ 
                                   %(scenarioDatabase, i[0], i[1], i[3], i[4])):
                    raise FileError, query.lastError().text()

                if not query.exec_("""delete from %s.person_synthetic_data where state = %s and county = %s """
                                   """ and tract = %s and bg = %s  """ 
                                   %(scenarioDatabase, i[0], i[1], i[3], i[4])):
                    raise FileError, query.lastError().text()
                a = self.project.synGeoIds.pop(i, -99)


            if reply == QMessageBox.Yes:
                print '------------------------------------------------------------------'
                print 'Generating synthetic population in Parallel...'


                dbList = ['%s' %self.project.db.hostname, '%s' %self.project.db.username, '%s' %self.project.db.password, '%s' %self.project.name]
                # breaking down the whole list into lists of 100 geographies each

                from math import floor

                geoCount = len(self.runGeoIds)
                binsize = 50

                bins = int(floor(geoCount/binsize))


                index = [(i*binsize, i*binsize+binsize) for i in range(bins)]
                index.append((bins*binsize, geoCount))


                for i in index:
                    
                    if self.gqAnalyzed and self.project.selVariableDicts.persControl:
                        print 'GQ ANALYZED WITH PERSON ATTRIBUTES CONTROLLED'
                        demo_parallel.run_parallel(self.job_server, self.project, self.runGeoIds[i[0]:i[1]], varCorrDict, controlAdjDict)
                    if self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                        print 'GQ ANALYZED WITH NO PERSON ATTRIBUTES CONTROLLED'
                        demo_parallel_noper.run_parallel(self.job_server, self.project, self.runGeoIds[i[0]:i[1]], varCorrDict, controlAdjDict)
                    if not self.gqAnalyzed and self.project.selVariableDicts.persControl:
                        print 'NO GQ ANALYZED WITH PERSON ATTRIBUTES CONTROLLED'
                        demo_parallel_nogqs.run_parallel(self.job_server, self.project, self.runGeoIds[i[0]:i[1]], varCorrDict, controlAdjDict)
                    if not self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                        print 'NO GQ ANALYZED WITH NO PERSON ATTRIBUTES CONTROLLED'
                        demo_parallel_nogqs_noper.run_parallel(self.job_server, self.project, self.runGeoIds[i[0]:i[1]], varCorrDict, controlAdjDict)
                    """
                    if self.gqAnalyzed:
                        demo_parallel.run_parallel(self.job_server, self.project, 
                                                   self.runGeoIds[i[0]:i[1]], dbList, varCorrDict, controlAdjDict)
                    else:
                        demo_parallel_nogqs.run_parallel(self.job_server, self.project, 
                                                         self.runGeoIds[i[0]:i[1]], dbList, varCorrDict, controlAdjDict)
                    """
                self.selGeographiesButton.setEnabled(False)
                for geo in self.runGeoIds:
                    self.project.synGeoIds[(geo[0], geo[1], geo[2], geo[3], geo[4])] = True

                    self.outputWindow.append("Running Syntheiss for geography State - %s, County - %s, Tract - %s, BG - %s"
                                             %(geo[0], geo[1], geo[3], geo[4]))

                print 'Completed generating synthetic population'
                print '------------------------------------------------------------------'

            elif reply == QMessageBox.No:
                print '------------------------------------------------------------------'
                print 'Generating synthetic population in Series...'

                for geo in self.runGeoIds:
                    self.project.synGeoIds[(geo[0], geo[1], geo[2], geo[3], geo[4])] = True

                    geo = Geography(geo[0], geo[1], geo[3], geo[4], geo[2])

                    self.outputWindow.append("Running Syntheiss for geography State - %s, County - %s, Tract - %s, BG - %s"
                                             %(geo.state, geo.county, geo.tract, geo.bg))


                    try:
                        if self.gqAnalyzed and self.project.selVariableDicts.persControl:
                            print 'GQ ANALYZED WITH PERSON ATTRIBUTES CONTROLLED'
                            demo.configure_and_run(self.project, geo, varCorrDict, controlAdjDict)
                        if self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                            print 'GQ ANALYZED WITH NO PERSON ATTRIBUTES CONTROLLED'
                            demo_noper.configure_and_run(self.project, geo, varCorrDict, controlAdjDict)
                        if not self.gqAnalyzed and self.project.selVariableDicts.persControl:
                            print 'NO GQ ANALYZED WITH PERSON ATTRIBUTES CONTROLLED'
                            demo_nogqs.configure_and_run(self.project, geo, varCorrDict, controlAdjDict)
                        if not self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                            print 'NO GQ ANALYZED WITH NO PERSON ATTRIBUTES CONTROLLED'
                            demo_nogqs_noper.configure_and_run(self.project, geo, varCorrDict, controlAdjDict)
                    except Exception, e:
                        self.outputWindow.append("\t- Error in the Synthesis for geography")
                        print ('Exception: %s' %e)

                self.selGeographiesButton.setEnabled(False)
            else:
                self.runGeoIds = []
                self.selGeographiesList.clear()

                print 'Completed generating synthetic population'
                print '------------------------------------------------------------------'

    def getPUMA5(self, geo):
        query = QSqlQuery(self.projectDBC.dbc)

        if not geo.puma5:
            if self.project.resolution == 'County':
                geo.puma5 = 99

            elif self.project.resolution == 'Tract':
                if not query.exec_("""select pumano from geocorr where state = %s and county = %s and tract = %s and bg = 1"""
                                   %(geo.state, geo.county, geo.tract)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]
            else:
                if not query.exec_("""select pumano from geocorr where state = %s and county = %s and tract = %s and bg = %s"""
                                   %(geo.state, geo.county, geo.tract, geo.bg)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]

        return geo

    def selGeographies(self):
        self.runGeoIds=[]
        geoids = self.allGeographyids()
        dia = VariableSelectionDialog(geoids, title = "Select Geographies", icon = "run", warning = "Note: Select geographies to synthesize")
        if dia.exec_():
            exists = True
            notoall = False

            if dia.selectedVariableListWidget.count() > 0:
                self.selGeographiesList.clear()
                for i in range(dia.selectedVariableListWidget.count()):
                    itemText = dia.selectedVariableListWidget.item(i).text()

                    item = re.split("[,]", itemText)
                    state, county, tract, bg = item
                    geo = Geography(int(state), int(county), int(tract), int(bg))
                    geo = self.getPUMA5(geo)

                    try:

                        if not exists:
                            raise DummyError, 'skip messagebox'

                        self.project.synGeoIds[(geo.state, geo.county, geo.puma5, geo.tract, geo.bg)]

                        if not notoall:
                            reply = QMessageBox.warning(self, "Run Synthesizer", """Synthetic population for """
                                                        """<b>State - %s, County - %s, PUMA5 - %s, Tract - %s, BG - %s</b> exists. """
                                                        """Would you like to re-run the synthesizer for the geography(s)?"""
                                                        %(geo.state, geo.county, geo.puma5, geo.tract, geo.bg),
                                                        QMessageBox.Yes| QMessageBox.No| QMessageBox.YesToAll| QMessageBox.NoToAll)
                            if reply == QMessageBox.Yes:
                                self.runGeoIds.append((geo.state, geo.county, geo.puma5, geo.tract, geo.bg))
                                self.selGeographiesList.addItem(itemText)
                                exists = True
                            elif reply == QMessageBox.No:
                                exists = True
                            elif reply == QMessageBox.YesToAll:
                                self.runGeoIds.append((geo.state, geo.county, geo.puma5, geo.tract, geo.bg))
                                self.selGeographiesList.addItem(itemText)
                                exists = False
                            elif reply == QMessageBox.NoToAll:
                                notoall = True

                    except Exception, e:
                        #print e
                        self.runGeoIds.append((geo.state, geo.county, geo.puma5, geo.tract, geo.bg))
                        self.selGeographiesList.addItem(itemText)
                if self.selGeographiesList.count()>0:
                    self.runSynthesizerButton.setEnabled(True)
                else:
                    self.runSynthesizerButton.setEnabled(False)
            else:
                self.selGeographiesList.clear()
                self.runSynthesizerButton.setEnabled(False)


    def allGeographyids(self):
        query = QSqlQuery(self.projectDBC.dbc)
        allGeoids = {}
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


            tract = 0
            bg = 0

            while query.next():
                state = query.value(STATE).toInt()[0]
                county = query.value(COUNTY).toInt()[0]

                if self.project.resolution == 'Tract' or self.project.resolution == 'Blockgroup' or self.project.resolution == 'TAZ':
                    tract = query.value(TRACT).toInt()[0]
                if self.project.resolution == 'Blockgroup' or self.project.resolution == 'TAZ':
                    bg = query.value(BG).toInt()[0]

                id = '%s,%s,%s,%s' %(state, county, tract, bg)
                idText = 'State - %s, County - %s, Tract - %s, Block Group - %s' %(state, county, tract, bg)

                allGeoids[id] = idText

        return allGeoids




    def prepareData(self):
        self.removeTables()
        self.project.synGeoIds = {}
        
        db = MySQLdb.connect(user = '%s' %self.project.db.username,
                             passwd = '%s' %self.project.db.password,
                             db = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario))

        try:
            if self.gqAnalyzed and self.project.selVariableDicts.persControl:
                prepare_data(db, self.project)
            if self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                prepare_data_noper(db, self.project)
            if not self.gqAnalyzed and self.project.selVariableDicts.persControl:
                prepare_data_nogqs(db, self.project)
            if not self.gqAnalyzed and not self.project.selVariableDicts.persControl:
                prepare_data_nogqs_noper(db, self.project)
                pass
        except KeyError, e:
            QMessageBox.warning(self, "Run Synthesizer", QString("""Check the <b>hhid, serialno</b> columns in the """
                                                                 """data. If you wish not to synthesize groupquarters, make"""
                                                                 """ sure that you delete all person records corresponding """
                                                                 """to groupquarters. In PopGen, when Census data is used, """
                                                                 """by default groupquarters need"""
                                                                 """ to be synthesized because person marginals include """
                                                                 """individuals living in households and groupquarters. Fix the data"""
                                                                 """ and run synthesizer again."""), 
                                QMessageBox.Ok)
            
            self.dialogButtonBox.emit(SIGNAL("accepted()"))
        db.commit()
        db.close()


    def removeTables(self):
        databaseName = self.project.name + 'scenario' + str(self.project.scenario)
        self.projectDBC.dbc.setDatabaseName(databaseName)
        self.projectDBC.dbc.open()

        tables = self.tableList()
        print tables
        query = QSqlQuery(self.projectDBC.dbc)
        for i in tables:
            if not query.exec_("""drop table %s""" %i):
                print "Warning: %s" %query.lastError().text()


        self.projectDBC.dbc.setDatabaseName(self.project.name)
        self.projectDBC.dbc.open()

    def tableList(self):
        tables = []

        query = QSqlQuery(self.projectDBC.dbc)
        if not query.exec_("""show tables"""):
            raise FileError, query.lastError.text()
        while query.next():
            tables.append('%s' %query.value(0).toString())
            
        return tables


    def isGqAnalyzed(self):
        if not self.project.gqVars:
            return False

        if self.project.sampleUserProv.userProv == False and self.project.controlUserProv.userProv == False:
            return True

        if self.project.sampleUserProv.userProv == True and self.project.sampleUserProv.gqLocation <> "":
            return True

        if self.project.controlUserProv.userProv == True and self.project.controlUserProv.gqLocation <> "":
            return True


        return False



    def readData(self):
        db = MySQLdb.connect(user = '%s' %self.project.db.username,
                             passwd = '%s' %self.project.db.password,
                             db = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario))
        dbc = db.cursor()

        dbc.execute("""select * from index_matrix_%s""" %(0))
        indexMatrix = numpy.asarray(dbc.fetchall())

        f = open('indexMatrix.pkl', 'wb')
        pickle.dump(indexMatrix, f)
        f.close()

        pIndexMatrix = person_index_matrix(db)
        f = open('pIndexMatrix.pkl', 'wb')
        pickle.dump(pIndexMatrix, f)
        f.close()

        dbc.close()
        db.close()



    def checkIfTableExists(self, tablename):
        # 0 - some other error, 1 - overwrite error (table deleted)
        if not self.query.exec_("""create table %s (dummy text)""" %tablename):
            if self.query.lastError().number() == 1050:
                reply = QMessageBox.question(None, "Processing Data",
                                             QString("""A table with name %s already exists. Would you like to overwrite?""" %tablename),
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
