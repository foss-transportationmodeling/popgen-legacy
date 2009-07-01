import sys
import numpy

from collections import defaultdict

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *


from database.createDBConnection import createDBC
from gui.misc.widgets import *


class SetCorrDialog(QDialog):
    def __init__(self, project, parent=None):
        super(SetCorrDialog, self).__init__(parent)

        self.setWindowTitle("Corresponding Sample Categories with Marginal Variables")
        self.setWindowIcon(QIcon("./images/varcorr.png"))
        import copy
        self.project = copy.deepcopy(project)
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.tabWidget = SetCorrTabWidget(self.project)


        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        correspondenceWarning = QLabel("""<font color = blue>Note: Select household/person/groupquarter variables of interest """
                                       """from the <b>'Sample Variable'</b> that you wish to control. Once these have been selected, """
                                       """create appropriate mapping between the categories of the selected variables and """
                                       """the columns in the marginal tables. To do this, highlight a category from the """
                                       """<b>'Selected Variable Categories'</b> and the corresponding column name under the """
                                       """<b>'Marginal Variables'</b> and click on <b>'Add Correspondence'</b>.</font>""")
        correspondenceWarning.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        layout.addWidget(correspondenceWarning)
        layout.addWidget(dialogButtonBox)
        self.setLayout(layout)

        hhldSelVariableDicts = copy.deepcopy(self.project.selVariableDicts.hhld)
        self.populate(hhldSelVariableDicts, self.tabWidget.housingTab)
        personSelVariableDicts = copy.deepcopy(self.project.selVariableDicts.person)
        self.populate(personSelVariableDicts, self.tabWidget.personTab)
        gqSelVariableDicts = copy.deepcopy(self.project.selVariableDicts.gq)
        self.populate(gqSelVariableDicts, self.tabWidget.gqTab)

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
                    if self.project.selVariableDicts.hhld <> self.tabWidget.housingTab.selVariables:
                        self.project.selVariableDicts.hhld = self.tabWidget.housingTab.selVariables
                        self.project.hhldVars, self.project.hhldDims =  self.checkIfRelationsDefined(self.project.selVariableDicts.hhld)
                        self.clearTables('hhld')
                    if self.project.selVariableDicts.person <> self.tabWidget.personTab.selVariables:
                        self.project.selVariableDicts.person = self.tabWidget.personTab.selVariables
                        self.project.personVars, self.project.personDims = self.checkIfRelationsDefined(self.project.selVariableDicts.person)
                        self.clearTables('person')
                    if self.project.selVariableDicts.gq <> self.tabWidget.gqTab.selVariables:
                        self.project.selVariableDicts.gq = self.tabWidget.gqTab.selVariables
                        self.project.gqVars, self.project.gqDims = self.checkIfRelationsDefined(self.project.selVariableDicts.gq, True)
                        self.clearTables('gq')
                    self.projectDBC.dbc.close()
                    QDialog.hide(self)
                    QDialog.accept(self)

    def clearTables(self, tableNamePrefix):
        #print "variable relations modified - %s" %(tableNamePrefix)
        self.projectDBC.dbc.open()
        query = QSqlQuery(self.projectDBC.dbc)
        if not query.exec_("""show tables"""):
            raise FileError, query.lastError().text()

        query1 = QSqlQuery(self.projectDBC.dbc)
         
        while query.next():
            tableName = query.value(0).toString()
            if tableName.startsWith(tableNamePrefix) and (tableName.endsWith("_joint_dist") or tableName.endsWith("_ipf")):
                if not query1.exec_("""drop table %s""" %(tableName)):
                    raise FileError, query1.lastError().text()


    def checkIfRelationsDefined(self, vardict, override=False):
        if len (vardict.keys()) > 0 or override:
            controlVariables = ['%s' %i for i in vardict.keys()]
            controlVariables.sort()
            #controlDimensions = numpy.asarray([len(vardict[QString(i)].keys()) for i in controlVariables])
            controlDimensions = numpy.asarray([len(vardict[i].keys()) for i in controlVariables])
            
            #print controlVariables, controlDimensions

            return controlVariables, controlDimensions        
        else:
            QMessageBox.warning(self, "Corresponding Sample Categories with Marginal Variables", """Control variables, and variable correspondence not defined appropriately. """
                                """Choose variables/ define relations and then run the synthesizer.""", QMessageBox.Ok)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)

class SetCorrTabWidget(QTabWidget):
    def __init__(self, project, parent=None):
        super(SetCorrTabWidget, self).__init__(parent)
        self.project = project

        layout = QVBoxLayout()
        

        tablesProject = self.tables()

        self.housingTab = TabWidgetItems(self.project, 'Household', 'hhld_marginals', 'hhld_sample')
        self.personTab = TabWidgetItems(self.project, 'Person', 'person_marginals', 'person_sample')

        self.addTab(self.housingTab, 'Household Variables')
        self.addTab(self.personTab, 'Person Variables')
        

        if self.isGqAnalyzed():
            self.gqTab = TabWidgetItems(self.project, 'Groupquarter', 'gq_marginals', 'gq_sample')
            self.addTab(self.gqTab, 'Groupquarters Variables')

        self.setLayout(layout)

        
    def isGqAnalyzed(self):
        if self.project.sampleUserProv.userProv == False and self.project.controlUserProv.userProv == False:
            return True
        
        if self.project.sampleUserProv.userProv == True and self.project.sampleUserProv.gqLocation <> "":
            return False
        
        if self.project.controlUserProv.userProv == True and self.project.controlUserProv.gqLocation <> "":
            return False
        


    def tables(self):
        projectDBC = createDBC(self.project.db, self.project.name)
        projectDBC.dbc.open()        

        tables = []
        query = QSqlQuery(projectDBC.dbc)
        if not query.exec_("""show tables"""):
            raise FileError, query.lastError().text()
        
        while query.next():
            tables.append('%s' %query.value(0).toString())
            
        projectDBC.dbc.close()
        return tables
            

class TabWidgetItems(QWidget):
    def __init__(self, project, controlType, controlTable, sampleTable, parent=None):
        super(TabWidgetItems, self).__init__(parent)
        
        self.project = project
        
        self.selVariables = defaultdict(dict)

        self.controlType = controlType

        self.controlTable = controlTable
        self.sampleTable = sampleTable

        self.sampleVarsDict = {}

        self.selVarCatStrings = {}
        self.relationStrings = {}

        sampleTableLabel = QLabel("Sample Table")
        sampleVarLabel = QLabel("Sample Variable")
        selSampleVarLabel = QLabel("Selected Variable")
        selSampleVarCatLabel = QLabel("Selected Variable Categories")
        self.sampleTableComboBox = QComboBox()
        self.sampleTableComboBox.setEnabled(False)

        self.sampleVarListWidget = ListWidget()
        self.selSampleVarListWidget = ListWidget()
        self.selSampleVarCatListWidget = ListWidget()
        self.selSampleVar = QPushButton("Select>>")
        self.selSampleVar.setEnabled(False)
        self.deselSampleVar = QPushButton("<<Deselect")
        self.deselSampleVar.setEnabled(False)

        
        vLayout4 = QVBoxLayout()
        vLayout4.addItem(QSpacerItem(10,50))
        vLayout4.addWidget(self.selSampleVar)
        vLayout4.addWidget(self.deselSampleVar)
        vLayout4.addItem(QSpacerItem(10,50))

                

        vLayout5 = QVBoxLayout()
        vLayout5.addWidget(sampleVarLabel)
        vLayout5.addWidget(self.sampleVarListWidget)


        vLayout6 = QVBoxLayout()
        vLayout6.addWidget(selSampleVarLabel)
        vLayout6.addWidget(self.selSampleVarListWidget)

        vLayout7 = QVBoxLayout()
        vLayout7.addWidget(selSampleVarCatLabel)
        vLayout7.addWidget(self.selSampleVarCatListWidget)


        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(vLayout5)
        hLayout2.addLayout(vLayout4)
        hLayout2.addLayout(vLayout6)
        hLayout2.addLayout(vLayout7)

        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(sampleTableLabel)
        vLayout2.addWidget(self.sampleTableComboBox)
        #vLayout2.addWidget(sampleVarLabel)
        vLayout2.addLayout(hLayout2)

        controlTableLabel = QLabel("Marginal Table")
        controlVarLabel = QLabel("Marginal Variables")
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

        relationLabel = QLabel("Correspondence between the Sample Variable Categories and the Marginal Variables")
        self.relationsListWidget = ListWidget()
        self.addRelation = QPushButton("Add Correspondence")
        self.deleteRelation = QPushButton("Delete Correspondence")
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
            QMessageBox.warning(self, "Corresponding Sample Categories with Marginal Variables",
                                """No variable was selected for %s control."""
                                """ Select variables and define relations to continue.""" %self.controlType, 
                                QMessageBox.Ok)
            return False
        else:
            return True
        

    def checkNumRelationsDefined(self):
        if self.relationsListWidget.count() <> self.selSampleVarCatListWidget.count():
            QMessageBox.warning(self, "Corresponding Sample Categories with Marginal Variables", 
                                """Insufficient correspondence defined for the selected <b>%s</b> control variable(s).""" %self.controlType,
                                QMessageBox.Ok)
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
        projectDBC = createDBC(self.project.db, self.project.name)
        projectDBC.dbc.open()

        variables = []
        query = QSqlQuery(projectDBC.dbc)
        if not query.exec_("""desc %s""" %tablename):
            raise FileError, query.lastError().text()
        
        FIELD = 0
        
        while query.next():
            field = query.value(FIELD).toString()
            variables.append(field)
            
        projectDBC.dbc.close()
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
            self.selVarCatStrings[i] = '%s' %varName

        self.selSampleVarCatListWidget.addItems(string)



    def categories(self, varname):
        projectDBC = createDBC(self.project.db, self.project.name)
        projectDBC.dbc.open()
        
        cats = []
        query = QSqlQuery(projectDBC.dbc)
        if not query.exec_("""select %s from %s group by %s""" %(varname, self.sampleSelTable, varname)):
            raise FileError, query.lastError().text()

        CATEGORY = 0

        while query.next():
            cat = unicode(query.value(CATEGORY).toString())

            cats.append(cat)
        self.sampleVarsDict['%s' %varname] = cats
        projectDBC.dbc.close()

    def varCatStrings(self, varName, varCats):
        string = []
        for i in varCats:
            string.append("%s, Category %s" %(varName, i))

        return string

    

    def removeSampleVarCats(self, item):
        varName = '%s' %item.text()

        for i in self.selVarCatStrings.keys():
            if self.selVarCatStrings[i] == varName:
                row = self.selSampleVarCatListWidget.rowOf(i)
                self.selSampleVarCatListWidget.takeItem(row)

        for i in self.relationStrings.keys():
            if self.relationStrings[i] == varName:
                row = self.relationsListWidget.rowOf(i)
                self.relationsListWidget.takeItem(row)
        try:
            self.selVariables.pop(varName)
        except Exception, e:
            #print e
            pass

    def addRelationAction(self):
        try:
            sampleVarCat = '%s' %self.selSampleVarCatListWidget.currentItem().text()
            controlVar = '%s' %self.controlVarListWidget.currentItem().text()
            varName = self.selVarCatStrings[sampleVarCat]

            try:
                controlVar = self.selVariables[varName][sampleVarCat]
                relation = '%s -  %s' %(sampleVarCat, controlVar)
                raise Exception, "The relation already exists"
            #print relation
            except Exception, e:
                #print '%s:%s' %(Exception, e)
                self.selVariables[varName][sampleVarCat] = controlVar
                relation = '%s -  %s' %(sampleVarCat, controlVar)
                self.relationStrings[relation] = varName
                
            row = self.relationsListWidget.rowOf(relation)
            itemAt = self.relationsListWidget.item(row)

            if row >= 0:
                QMessageBox.warning(self, "Corresponding Sample Categories with Marginal Variables", """If you wish to change the control variable """
                                    """corresponding to a category of the control variable, delete the existing correspondence """
                                    """and define again.""", QMessageBox.Ok)
                self.relationsListWidget.setCurrentItem(itemAt)
            else:
                self.relationsListWidget.addItem(relation)

        except Exception, e:
            QMessageBox.warning(self, "Corresponding Sample Categories with Marginal Variables", """Select a variable category """
                                """and a variable name to add a relation.""", QMessageBox.Ok)
            



    def deleteRelationAction(self):
        if len(self.relationsListWidget.selectedItems()) >0:
            self.deleteRelation.setEnabled(True)

    def deleteRelationNow(self):
        self.parseRelation(self.relationsListWidget.currentItem())
        self.relationsListWidget.remove()
        #print self.selVariables


        
    def parseRelation(self, item):
        relation = '%s' %item.text()
        for i in self.selVariables.keys():
            for j in self.selVariables[i].keys():
                matchRelation = '%s -  %s' %(j, self.selVariables[i][j])
                if matchRelation == relation:
                    self.selVariables[i].pop(j)

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
