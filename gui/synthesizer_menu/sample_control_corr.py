import sys
from collections import defaultdict

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *


from database.createDBConnection import createDBC
from gui.misc.widgets import *


class SetCorrDialog(QDialog):
    def __init__(self, project, parent=None):
        super(SetCorrDialog, self).__init__(parent)
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.filename)
        self.projectDBC.dbc.open()

        self.tabWidget = SetCorrTabWidget(self.project)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        layout.addWidget(dialogButtonBox)
        self.setLayout(layout)

        self.populate(self.project.selVariables.hhld, self.tabWidget.housingTab)
        self.populate(self.project.selVariables.person, self.tabWidget.personTab)
        self.populate(self.project.selVariables.gq, self.tabWidget.gqTab)

        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))        



    def populate(self, selVariable, tab):

        for i in selVariable.keys():
            tab.selSampleVarListWidget.addItem(i)
            row = tab.sampleVarListWidget.rowOf(i)
            tab.sampleVarListWidget.setCurrentRow(row)
            tab.sampleVarListWidget.remove()
            cats = []
            for j in selVariable[i].keys():

                varCatString = j

                dummy = ('%s' %j).split()

                sampleVarCat = dummy[-1]
                varName = i
                controlVar = selVariable[i][varCatString]

                relation = '%s -  %s' %(varCatString, controlVar)
                
                tab.selVarCatStrings[varCatString] = varName
                tab.relationStrings[relation] = varName
                tab.selVariables = selVariable

                tab.selSampleVarCatListWidget.addItem(varCatString)
                tab.relationsListWidget.addItem(relation)

                cats.append(sampleVarCat)
            tab.sampleVarsDict[i] = cats       



    def accept(self):
        if self.tabWidget.housingTab.check():
            if self.tabWidget.personTab.check():
                if self.tabWidget.gqTab.checkNumRelationsDefined():
                    self.project.selVariables.hhld = self.tabWidget.housingTab.selVariables
                    self.project.selVariables.person = self.tabWidget.personTab.selVariables
                    self.project.selVariables.gq = self.tabWidget.gqTab.selVariables
                    self.projectDBC.dbc.close()
                    QDialog.hide(self)
                    QDialog.accept(self)


    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)

class SetCorrTabWidget(QTabWidget):
    def __init__(self, project, parent=None):
        super(SetCorrTabWidget, self).__init__(parent)
        self.project = project

        layout = QVBoxLayout()
        

        tablesProject = self.tables()

        housingSampleVars = {'first':[1,2,3,4],
                             'second': [-99, 1, 2, 3]}
        
        housingControlVars = ['first1', 'first2', 'first3', 'first4', 'second-99', 'second11', 'second2', 'second3']

        personSampleVars = {'pfirst':[1,2,3,-99],
                             'psecond': [-99, 2, 3,23]}

        personControlVars = ['pirst1', 'pirst2', 'pirst3', 'pirst-99', 'psecond-99', 'psecond11', 'psecond2', 'psecond23']

        
        self.housingTab = TabWidgetItems('Household', 'hhld_marginals', 'hhld_sample')
        self.gqTab = TabWidgetItems('Group Quarter', 'gq_marginals', 'gq_sample')
        self.personTab = TabWidgetItems('Person', 'person_marginals', 'person_sample')


        self.addTab(self.housingTab, 'Housing Variables')
        self.addTab(self.personTab, 'Person Variables')
        self.addTab(self.gqTab, 'Group Quarters Variables')

        self.setLayout(layout)

        

    def tables(self):
        tables = []
        query = QSqlQuery()
        if not query.exec_("""show tables"""):
            raise FileError, query.lastError().text()
        
        while query.next():
            tables.append('%s' %query.value(0).toString())
            
        return tables
            

class TabWidgetItems(QWidget):
    def __init__(self, controlType, controlTable, sampleTable, parent=None):
        super(TabWidgetItems, self).__init__(parent)
        
        self.selVariables = defaultdict(dict)

        self.controlType = controlType

        self.controlTable = controlTable
        self.sampleTable = sampleTable

        self.sampleVarsDict = {}

        self.selVarCatStrings = {}
        self.relationStrings = {}

        sampleTableLabel = QLabel("Sample Table")
        sampleVarLabel = QLabel("Sample Variable")
        self.sampleTableComboBox = QComboBox()
        self.sampleTableComboBox.setEnabled(False)

        self.sampleVarListWidget = ListWidget()
        self.selSampleVarListWidget = ListWidget()
        self.selSampleVarCatListWidget = ListWidget()
        self.selSampleVar = QPushButton(">>")
        self.selSampleVar.setEnabled(False)
        self.deselSampleVar = QPushButton("<<")
        self.deselSampleVar.setEnabled(False)

        
        vLayout4 = QVBoxLayout()
        vLayout4.addItem(QSpacerItem(10,50))
        vLayout4.addWidget(self.selSampleVar)
        vLayout4.addWidget(self.deselSampleVar)
        vLayout4.addItem(QSpacerItem(10,50))
        

        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(self.sampleVarListWidget)
        hLayout2.addLayout(vLayout4)
        hLayout2.addWidget(self.selSampleVarListWidget)
        hLayout2.addWidget(self.selSampleVarCatListWidget)

        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(sampleTableLabel)
        vLayout2.addWidget(self.sampleTableComboBox)
        vLayout2.addWidget(sampleVarLabel)
        vLayout2.addLayout(hLayout2)

        controlTableLabel = QLabel("Control Table")
        controlVarLabel = QLabel("Control Variables")
        self.controlTableComboBox = QComboBox()
        self.controlTableComboBox.setEnabled(False)
        self.controlVarListWidget = ListWidget()

        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(controlTableLabel)
        vLayout3.addWidget(self.controlTableComboBox)
        vLayout3.addWidget(controlVarLabel)
        vLayout3.addWidget(self.controlVarListWidget)


        hLayout1 = QHBoxLayout()
        hLayout1.addLayout(vLayout2)
        hLayout1.addLayout(vLayout3)

        relationLabel = QLabel("Relationships between the Sample Variable Categories and the Control Variables")
        self.relationsListWidget = ListWidget()
        self.addRelation = QPushButton("Add Relation")
        self.deleteRelation = QPushButton("Delete Relation")
        self.deleteRelation.setEnabled(False)

        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(self.addRelation)
        vLayout3.addWidget(self.deleteRelation)
        vLayout3.addItem(QSpacerItem(10,100))


        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(self.relationsListWidget)
        hLayout2.addLayout(vLayout3)


        layout = QVBoxLayout()
        layout.addLayout(hLayout1)
        layout.addWidget(relationLabel)
        layout.addLayout(hLayout2)

        
        self.setLayout(layout)

        self.connect(self.addRelation, SIGNAL("clicked()"), self.addRelationAction)
        self.connect(self.relationsListWidget, SIGNAL("itemSelectionChanged()"), self.deleteRelationAction)
        self.connect(self.sampleVarListWidget, SIGNAL("itemSelectionChanged()"), self.enableSelButton)
        self.connect(self.selSampleVarListWidget, SIGNAL("itemSelectionChanged()"), self.enableDeselButton)
        self.connect(self, SIGNAL("addSampleVar(QListWidgetItem *)"), self.addSampleVarCats)
        self.connect(self, SIGNAL("removeSampleVar(QListWidgetItem *)"), self.removeSampleVarCats)
        self.connect(self.selSampleVar, SIGNAL("clicked()"), self.moveSelVars)
        self.connect(self.deselSampleVar, SIGNAL("clicked()"), self.moveDeselVars)
        self.connect(self.deleteRelation, SIGNAL("clicked()"), self.deleteRelationNow)
        self.connect(self.sampleTableComboBox, SIGNAL("highlighted(int)"), self.populateSampleVariables)
        self.connect(self.controlTableComboBox, SIGNAL("highlighted(int)"), self.populateControlVariables)
        
        self.populate()

        
        
    def check(self):
        check = self.checkSelectedVariables() and self.checkNumRelationsDefined()
        
        return check

        


    def checkSelectedVariables(self):
        if not (self.selSampleVarListWidget.count() > 0):
            QMessageBox.warning(self, QString("PopSim: Synthesizer Inputs"),
                                QString("""No variable was selected for %s control."""
                                        """ Please select variables and define relations to continue.""" %self.controlType))
            return False
        else:
            return True
        

    def checkNumRelationsDefined(self):
        if self.relationsListWidget.count() <> self.selSampleVarCatListWidget.count():
            QMessageBox.warning(self, QString("PopSim: Synthesizer Inputs"), 
                                QString("""Not enough relations defined for the %s control.""" %self.controlType))
            return False
        else:
            return True


    def populateSampleVariables(self, index):
        self.sampleSelTable = self.sampleTableComboBox.itemText(index)
        self.sampleVars = self.variablesInTable(self.sampleSelTable)
        self.sampleVarListWidget.clear()
        self.selSampleVarListWidget.clear()
        self.selSampleVarCatListWidget.clear()
        self.sampleVarListWidget.addItems(self.sampleVars)


    def populateControlVariables(self, index):
        self.controlSelTable = self.controlTableComboBox.itemText(index)
        self.controlVars = self.variablesInTable(self.controlSelTable)
        self.controlVarListWidget.clear()
        self.controlVarListWidget.addItems(self.controlVars)
        

    def variablesInTable(self, tablename):
        variables = []
        query = QSqlQuery()
        if not query.exec_("""desc %s""" %tablename):
            raise FileError, query.lastError().text()
        
        FIELD = 0
        
        while query.next():
            field = query.value(FIELD).toString()
            variables.append(field)
            
        return variables

    def enableSelButton(self):
        if len(self.sampleVarListWidget.selectedItems())>0:
            self.selSampleVar.setEnabled(True)
        else:
            self.selSampleVar.setEnabled(False)

    def enableDeselButton(self):
        if len(self.selSampleVarListWidget.selectedItems())>0:
            self.deselSampleVar.setEnabled(True)
        else:
            self.deselSampleVar.setEnabled(False)


    def moveSelVars(self):
        item = self.sampleVarListWidget.currentItem()
        self.sampleVarListWidget.remove()
        self.selSampleVarListWidget.addItem(item)
        self.emit(SIGNAL("addSampleVar(QListWidgetItem *)"), item)

    def moveDeselVars(self):
        item = self.selSampleVarListWidget.currentItem()
        self.selSampleVarListWidget.remove()
        self.sampleVarListWidget.addItem(item)
        self.emit(SIGNAL("removeSampleVar(QListWidgetItem *)"), item)


    def addSampleVarCats(self, item):
        varName = item.text()

        self.categories(varName)
        varCats = self.sampleVarsDict['%s' %varName]

        string = self.varCatStrings(varName, varCats)

        for i in string:
            self.selVarCatStrings[i] = varName

        self.selSampleVarCatListWidget.addItems(string)



    def categories(self, varname):
        cats = []
        query = QSqlQuery()
        if not query.exec_("""select %s from %s group by %s""" %(varname, self.sampleSelTable, varname)):
            raise FileError, query.lastError().text()

        CATEGORY = 0

        while query.next():
            cat = unicode(query.value(CATEGORY).toString())

            cats.append(cat)
        self.sampleVarsDict['%s' %varname] = cats


    def varCatStrings(self, varName, varCats):
        string = []
        for i in varCats:
            string.append("%s, Category %s" %(varName, i))

        return string

    

    def removeSampleVarCats(self, item):
        varName = item.text()

        for i in self.selVarCatStrings.keys():
            if self.selVarCatStrings[i] == varName:
                row = self.selSampleVarCatListWidget.rowOf(i)
                self.selSampleVarCatListWidget.takeItem(row)

        for i in self.relationStrings.keys():
            if self.relationStrings[i] == varName:
                row = self.relationsListWidget.rowOf(i)
                self.relationsListWidget.takeItem(row)

        self.selVariables.pop(varName)
            


    def addRelationAction(self):
        sampleVarCat = self.selSampleVarCatListWidget.currentItem().text()
        varName = self.selVarCatStrings['%s' %sampleVarCat]
        controlVar = self.controlVarListWidget.currentItem().text()

        relation = '%s -  %s' %(sampleVarCat, controlVar)

        self.selVariables[varName][sampleVarCat] = controlVar

        self.relationStrings[relation] = varName
        
        row = self.relationsListWidget.rowOf(relation)
        if row >0:
            self.relationsListWidget.setItemSelected(itemAt, True)
        else:
            self.relationsListWidget.addItem(relation)


    def deleteRelationAction(self):
        if len(self.relationsListWidget.selectedItems()) >0:
            self.deleteRelation.setEnabled(True)

    def deleteRelationNow(self):
        self.parseRelation(self.relationsListWidget.currentItem())
        self.relationsListWidget.remove()


        
    def parseRelation(self, item):
        relation = item.text()
        for i in self.selVariables.keys():
            if i == relation:
                self.selVariables.pop(i)


    def populate(self):
        self.sampleTableComboBox.addItem(self.sampleTable)
        self.controlTableComboBox.addItem(self.controlTable)
        self.sampleTableComboBox.emit(SIGNAL("highlighted(int)"), 0)
        self.controlTableComboBox.emit(SIGNAL("highlighted(int)"), 0)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = 1
    form = SetCorrDialog(a)
    #form = TabWidget(a)
    form.show()
    app.exec_()
