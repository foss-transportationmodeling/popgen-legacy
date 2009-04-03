import urllib
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
from misc.errors import FileError
from misc.utils import UnzipFile
from import_data import ImportUserProvData, FileProperties

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
        self.states()
        self.stateAbbreviations()


        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.query = QSqlQuery(self.projectDBC.dbc)


        self.downloadPUMSData()
        self.createPUMSTable()


    def states(self):
        self.statesSelected = []
        for i in self.project.region.keys():
            try:
                self.statesSelected.index(self.project.region[i])
            except ValueError, e:
                self.statesSelected.append(self.project.region[i])



    def stateAbbreviations(self):
        file = QFile("./data/counties.csv")

        if not file.open(QIODevice.ReadOnly):
            raise IOError, unicode(file.errorString())

        self.stateAbb = {}
        self.stateCode = {}
        while not file.atEnd():
            a = file.readLine()
            a = a.split(",")
            self.stateAbb[a[1]] = a[4][:-2]
            code = '%s'%a[0]
            code = code.rjust(2, '0')
            self.stateCode[a[1]] = code

        file.close()


    def downloadPUMSData(self):
        for i in self.statesSelected:
            try:
                os.makedirs("C:/PopSim/data/%s/PUMS"%i)
                self.retrieveAndStorePUMS(i)
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
                        self.retrieveAndStorePUMS(i)

            #self.extractPUMS(i)


    def retrieveAndStorePUMS(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')
        urllib.urlretrieve("""http://ftp2.census.gov/census_2000/datasets/"""
                           """PUMS/FivePercent/%s/all_%s.zip""" %(web_state, web_state),
                           "C:/PopSim/data/%s/PUMS/all_%s.zip" %(state, web_state))

    def extractPUMS(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')
        file = UnzipFile("C:/PopSim/data/%s/PUMS" %(state), "all_%s.zip" %(web_state))
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


        for i in self.statesSelected:
            if not self.query.exec_("""create table pumsraw%s (raw TEXT)""" %self.stateAbb[i]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""load data local infile 'C:/PopSim/data/%s/PUMS/PUMS5_%s.TXT' """
                                    """into table pumsraw%s""" %(i, self.stateCode[i], self.stateAbb[i])):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""alter table pumsraw%s add column recordtype char(1)""" %self.stateAbb[i]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update pumsraw%s set recordtype = left(raw, 1)""" %self.stateAbb[i]):
                raise FileError, self.query.lastError().text()

    def createHousingPUMSTable(self):
        for i in self.statesSelected:
            if not self.query.exec_("""create table pumsrawhousing%s select raw from pumsraw%s where recordtype = 'H'""" %(self.stateAbb[i],self.stateAbb[i])):
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
                                                 len(self.statesSelected)*len(self.housingVariablesSelected))
                progressDialog.setMinimumSize(275,125)
                progress = 0
                for i in self.statesSelected:
                    # Make a copy of the raw housing pums file
                    if not self.query.exec_("""create table housing_pums_%s select * from pumsrawhousing%s"""
                                            %(self.stateAbb[i], self.stateAbb[i])):
                        raise FileError, self.query.lastError().text()
                    # Extract the selected variables from the copy of the housing pums file

                    for j in self.housingVariablesSelected:
                        if not self.query.exec_("""alter table housing_pums_%s add column %s text""" %(self.stateAbb[i], j)):
                            raise FileError, self.query.lastError().text()

                        if not self.query.exec_("""update housing_pums_%s set %s = mid(raw, %s, %s)"""
                                                %(self.stateAbb[i], j, housingVarBegDict['%s'%j], housingVarLenDict['%s'%j])):
                            raise FileError, self.query.lastError().text()
                        progress = progress + 1
                        progressDialog.setValue(progress)



    def createPersonPUMSTable(self):

        for i in self.statesSelected:
            if not self.query.exec_("""create table pumsrawperson%s select raw from pumsraw%s where recordtype = 'P'"""
                                    %(self.stateAbb[i],self.stateAbb[i])):
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
                                                 len(self.statesSelected)*len(self.personVariablesSelected))
                progressDialog.setMinimumSize(275,125)
                progress = 0
                for i in self.statesSelected:
                    # Make a copy of the raw person pums file
                    if not self.query.exec_("""create table person_pums_%s select * from pumsrawperson%s"""
                                            %(self.stateAbb[i], self.stateAbb[i])):
                        raise FileError, self.query.lastError().text()
                    # Extract the selected variables from the copy of the person pums file
                    for j in self.personVariablesSelected:
                        if not self.query.exec_("""alter table person_pums_%s add column %s text""" %(self.stateAbb[i], j)):
                            raise FileError, self.query.lastError().text()

                        if not self.query.exec_("""update person_pums_%s set %s = mid(raw, %s, %s)"""
                                                %(self.stateAbb[i], j, personVarBegDict['%s'%j], personVarLenDict['%s'%j])):
                            raise FileError, self.query.lastError().text()
                        progress = progress + 1
                        progressDialog.setValue(progress)

class ListWidget(QListWidget):
    def __init__(self, variables, parent = None):
        super(ListWidget, self).__init__(parent)
        self.variables = variables

    def populate(self):
        self.clear()
        if len(self.variables) > 0:
            self.addItems(self.variables)

        self.sortItems()

class VariableSelectionDialog(QDialog):
    def __init__(self, variableDict, defaultVariables, title="", icon="", parent=None):
        super(VariableSelectionDialog, self).__init__(parent)

        self.defaultVariables = defaultVariables
        self.variableDict = variableDict
        self.variables = self.variableDict.keys()

        self.checkDefaultVariables()

        self.setStatusTip("Dummy String")
        self.setFixedSize(QSize(500,300))

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Reset| QDialogButtonBox.RestoreDefaults| QDialogButtonBox.Cancel| QDialogButtonBox.Ok)
        layout = QVBoxLayout()

        selectButton = QPushButton('Select>>')
        unselectButton = QPushButton('<<Unselect')
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(selectButton)
        buttonLayout.addWidget(unselectButton)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("../images/%s.png"%(icon)))

        self.oriVariables = self.variables

        self.variableListWidget = ListWidget(self.variables)
        self.variableListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selectedVariableListWidget = ListWidget([])
        self.selectedVariableListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.variableDescLabel = QLabel("Description of the variables")


        hLayout = QHBoxLayout()
        hLayout.addWidget(self.variableListWidget)
        hLayout.addLayout(buttonLayout)
        hLayout.addWidget(self.selectedVariableListWidget)

        layout.addLayout(hLayout)
        layout.addWidget(self.variableDescLabel)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)

        self.variableListWidget.populate()


        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(dialogButtonBox, SIGNAL("clicked(QAbstractButton *)"), self.resetandrestore)
        self.connect(selectButton, SIGNAL("clicked()"), self.moveSelected)
        self.connect(unselectButton, SIGNAL("clicked()"), self.moveUnselected)
        self.connect(self.variableListWidget, SIGNAL("currentRowChanged(int)"), self.displayVariableDescription)
        self.connect(self.selectedVariableListWidget, SIGNAL("currentRowChanged(int)"), self.displaySelectedVariableDescription)

    def displayVariableDescription(self, row):
        if row is not -1:
            self.variableDescLabel.setText('%s'%self.variableDict['%s'%self.variableListWidget.item(row).text()])

    def displaySelectedVariableDescription(self, row):
        if row is not -1:
            self.variableDescLabel.setText('%s'%self.variableDict['%s'%self.selectedVariableListWidget.item(row).text()])



    def checkDefaultVariables(self):
        diff = [var for var in self.defaultVariables if var not in self.variables]
        if len(diff) >0 :
            raise FileError, "The default variable list contains variable names that are not in the variable list. "


    def resetandrestore(self, button):
        if button.text() == 'Restore Defaults':
            # Moving the selected variable list to the unselected list
            for i in self.selectedVariableListWidget.variables:
                self.variableListWidget.variables.append(i)
            self.variableListWidget.populate()
            # Emptying the selected variable list
            self.selectedVariableListWidget.variables = []
            self.selectedVariableListWidget.populate()

            # Removing default variables from the unselected list
            for i in self.defaultVariables:
                self.variableListWidget.variables.remove(i)
            self.variableListWidget.populate()

            # Populating the selected variable list with the default variables
            import copy
            self.selectedVariableListWidget.variables = copy.deepcopy(self.defaultVariables)
            self.selectedVariableListWidget.populate()

        if button.text() == 'Reset':
            for i in self.selectedVariableListWidget.variables:
                self.variableListWidget.variables.append(i)

            self.selectedVariableListWidget.variables = []
            self.selectedVariableListWidget.populate()
            self.variableListWidget.populate()

    def moveSelected(self):
        selectedItems = self.variableListWidget.selectedItems()
        for i in selectedItems:
            self.variableListWidget.variables.remove(i.text())
            self.selectedVariableListWidget.variables.append(i.text())

        self.variableListWidget.populate()
        self.selectedVariableListWidget.populate()
        print 'moveselec', self.defaultVariables

    def moveUnselected(self):
        unselectedItems = self.selectedVariableListWidget.selectedItems()
        for i in unselectedItems:
            self.selectedVariableListWidget.variables.remove(i.text())
            self.variableListWidget.variables.append(i.text())

        self.variableListWidget.populate()
        self.selectedVariableListWidget.populate()
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    vars = {'a':'first', 'b':'second', 'c':'third', 'd':'fourth'}
    defvars = ['a','b']
    dlg = VariableSelectionDialog(vars, defvars)
    dlg.exec_()
