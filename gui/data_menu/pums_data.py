import urllib
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
from misc.errors import FileError
from misc.utils import UnzipFile
from misc.widgets import VariableSelectionDialog
from import_data import ImportUserProvData, FileProperties

from global_vars import *

class UserImportSampleData():
    def __init__(self, project):
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.query = QSqlQuery(self.projectDBC.dbc)

    def createHhldTable(self):
        hhldTableQuery = self.mysqlQueries('hhld_sample', self.project.sampleUserProv.hhLocation)
        
        if not self.query.exec_(hhldTableQuery.query1):
            raise FileError, self.query.lastError().text()
        
        if not self.query.exec_(hhldTableQuery.query2):
            raise FileError, self.query.lastError().text()


    def createGQTable(self):
        gqLocLen = len(self.project.sampleUserProv.gqLocation)
        
        if gqLocLen > 1:
            gqTableQuery = self.mysqlQueries('gq_sample', self.project.sampleUserProv.gqLocation)

            if not self.query.exec_(gqTableQuery.query1):
                raise FileError, self.query.lastError().text()
            
            if not self.query.exec_(gqTableQuery.query2):
                raise FileError, self.query.lastError().text()

    
    def createPersonTable(self):
        personTableQuery = self.mysqlQueries('person_sample', self.project.sampleUserProv.personLocation)

        if not self.query.exec_(personTableQuery.query1):
            raise FileError, self.query.lastError().text()
        
        if not self.query.exec_(personTableQuery.query2):
            raise FileError, self.query.lastError().text()

    def mysqlQueries(self, name, filePath):
        fileProp = FileProperties(filePath)
        fileQuery = ImportUserProvData(name,
                                       filePath,
                                       fileProp.varNames,
                                       fileProp.varTypes,
                                       fileProp.varNamesDummy,
                                       fileProp.varTypesDummy)
        return fileQuery

class AutoImportPUMSData():
    def __init__(self, project):
        self.project = project
        self.state = self.project.state
        self.stateAbb = self.project.stateAbb
        self.stateCode = self.project.stateCode


        self.loc = DATA_DOWNLOAD_LOCATION + os.path.sep + self.state + os.path.sep + 'PUMS'
        self.loc = os.path.realpath(self.loc)

        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.query = QSqlQuery(self.projectDBC.dbc)


        self.downloadPUMSData()
        self.createPUMSTable()


    def downloadPUMSData(self):

        try:
            os.makedirs(self.loc)
            self.retrieveAndStorePUMS(self.state)
        except WindowsError, e:
            reply = QMessageBox.question(None, "PopSim: Processing Data",
                                         QString("""Windows Error: %s.\n\n"""
                                                 """Do you wish to keep the existing files?"""
                                                 """\nPress No if you wish to download the files again."""%e),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "PopSim: Processing Data",
                                               QString("""Are you sure you want to continue?"""),
                                               QMessageBox.Yes|QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    self.retrieveAndStorePUMS(self.state)

            #self.extractPUMS(self.state)


    def retrieveAndStorePUMS(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')
        download_location = self.loc + os.path.sep + 'all_%s.zip' %(web_state)
        urllib.urlretrieve("""http://ftp2.census.gov/census_2000/datasets/"""
                           """PUMS/FivePercent/%s/all_%s.zip""" %(web_state, web_state),
                           download_location)

    def extractPUMS(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')

        file = UnzipFile(self.loc, "all_%s.zip" %(web_state))
        file.unzip()

    def createPUMSTable(self):

        # Creats a table that contains the location of the different PUMS variables in the raw data files
        PUMSVariableDefTable = ImportUserProvData("PUMS2000VariableList",
                                                  "./data/PUMS2000_Variables.csv",
                                                  [], [],True, True)

        if not self.query.exec_(PUMSVariableDefTable.query1):
            raise FileError, self.query.lastError().text()

        if not self.query.exec_(PUMSVariableDefTable.query2):
            raise FileError, self.query.lastError().text()

        if not self.query.exec_("""create table pumsraw%s (raw TEXT)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        pums_loc = self.loc + os.path.sep + 'PUMS5_%s.TXT' %(self.stateCode[self.state])
        pums_loc = pums_loc.replace("\\", "/")
        if not self.query.exec_("""load data local infile '%s' """
                                """into table pumsraw%s""" %(pums_loc, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""alter table pumsraw%s add column recordtype char(1)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update pumsraw%s set recordtype = left(raw, 1)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()

    def createHousingPUMSTable(self):
        if not self.query.exec_("""create table pumsrawhousing%s select raw from pumsraw%s where recordtype = 'H'""" 
                                %(self.stateAbb[self.state],self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()

        # Reading the list of PUMS housing variable names
        if not self.query.exec_("""select variablename, description, beginning, length from pums2000variablelist where type = 'H'"""):
            raise FileError, self.query.lastError().text()
        else:
            housingVariableDict = {}
            housingVarBegDict = {}
            housingVarLenDict = {}
            while (self.query.next()):
                housingVariableDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(1).toString()
                housingVarBegDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(2).toString()
                housingVarLenDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(3).toString()



        # Reading the list of PUMS default housing variable names
        if not self.query.exec_("""select variablename from pums2000variablelist where type = 'H' and defaultvar = 1"""):
            raise FileError, self.query.lastError().text()
        else:
            housingDefaultVariables = []
            while (self.query.next()):
                housingDefaultVariables.append(self.query.value(0).toString())

                housingVariablesDialog = VariableSelectionDialog(housingVariableDict, housingDefaultVariables,
                                                                 "PUMS Housing Variable Selection",
                                                                 "controlvariables")

            # Launch a dialogbox to select the housing variables of interest
            if housingVariablesDialog.exec_():
                self.housingVariablesSelectedDummy = True
                self.housingVariablesSelected = housingVariablesDialog.selectedVariableListWidget.variables
            else:
                self.housingVariablesSelectedDummy = False
                QMessageBox.information(None, "PopSim: Processing Data", QString("""No PUMS person variables are selected."""
                                                                 """Please start the data import process again to proceed. """),
                                        QMessageBox.Ok)

            if self.housingVariablesSelectedDummy:
                progressDialog = QProgressDialog("Creating Housing PUMS Tables in MySQL...", "Abort", 1,
                                                 len(self.housingVariablesSelected))
                progressDialog.setMinimumSize(275,125)
                progress = 0
                # Make a copy of the raw housing pums file
                if not self.query.exec_("""create table housing_pums_%s select * from pumsrawhousing%s"""
                                        %(self.stateAbb[self.state], self.stateAbb[self.state])):
                    raise FileError, self.query.lastError().text()
                # Extract the selected variables from the copy of the housing pums file
                
                for j in self.housingVariablesSelected:
                    if not self.query.exec_("""alter table housing_pums_%s add column %s text""" 
                                            %(self.stateAbb[self.state], j)):
                        raise FileError, self.query.lastError().text()
                    
                    if not self.query.exec_("""update housing_pums_%s set %s = mid(raw, %s, %s)"""
                                            %(self.stateAbb[self.state], j, 
                                              housingVarBegDict['%s'%j], housingVarLenDict['%s'%j])):
                        raise FileError, self.query.lastError().text()
                    progress = progress + 1
                    progressDialog.setValue(progress)



    def createPersonPUMSTable(self):
        if not self.query.exec_("""create table pumsrawperson%s select raw from pumsraw%s where recordtype = 'P'"""
                                %(self.stateAbb[self.state],self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()

        # Reading the list of PUMS person variable names
        if not self.query.exec_("""select variablename, description, beginning, length from pums2000variablelist where type = 'P'"""):
            raise FileError, self.query.lastError().text()
        else:
            personVariableDict = {}
            personVarBegDict = {}
            personVarLenDict = {}
            while (self.query.next()):
                personVariableDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(1).toString()
                personVarBegDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(2).toString()
                personVarLenDict['%s'%self.query.value(0).toString()] = '%s'%self.query.value(3).toString()

        # Reading the list of PUMS default person variable names
        if not self.query.exec_("""select variablename from pums2000variablelist where type = 'P' and defaultvar = 1"""):
            raise FileError, self.query.lastError().text()
        else:
            personDefaultVariables = []
            while (self.query.next()):
                personDefaultVariables.append(self.query.value(0).toString())

                personVariablesDialog = VariableSelectionDialog(personVariableDict, personDefaultVariables,
                                                                 "PUMS Person Variable Selection",
                                                                 "controlvariables")

            # Launch a dialogbox to select the person variables of interest
            if personVariablesDialog.exec_():
                self.personVariablesSelectedDummy = True
                self.personVariablesSelected = personVariablesDialog.selectedVariableListWidget.variables

            else:
                self.personVariablesSelectedDummy = False
                QMessageBox.information(None, "PopSim: Processing Data", QString("""No PUMS person variables are selected."""
                                                                 """Please start the data import process again to proceed. """),
                                        QMessageBox.Ok)

            if self.personVariablesSelectedDummy:
                progressDialog = QProgressDialog("Creating Person PUMS Tables in MySQL...", "Abort", 1,
                                                 len(self.personVariablesSelected))
                progressDialog.setMinimumSize(275,125)
                progress = 0
                # Make a copy of the raw person pums file
                if not self.query.exec_("""create table person_pums_%s select * from pumsrawperson%s"""
                                        %(self.stateAbb[self.state], self.stateAbb[self.state])):
                    raise FileError, self.query.lastError().text()
                    # Extract the selected variables from the copy of the person pums file
                for j in self.personVariablesSelected:
                    if not self.query.exec_("""alter table person_pums_%s add column %s text""" 
                                            %(self.stateAbb[self.state], j)):
                        raise FileError, self.query.lastError().text()
                    
                    if not self.query.exec_("""update person_pums_%s set %s = mid(raw, %s, %s)"""
                                            %(self.stateAbb[self.state], j, 
                                              personVarBegDict['%s'%j], personVarLenDict['%s'%j])):
                        raise FileError, self.query.lastError().text()
                    progress = progress + 1
                    progressDialog.setValue(progress)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    vars = {'a':'first', 'b':'second', 'c':'third', 'd':'fourth'}
    defvars = ['a','b']
    dlg = VariableSelectionDialog(vars, defvars)
    dlg.exec_()
