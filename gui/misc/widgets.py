# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from misc.map_toolbar import *
import re
from gui.misc.errors import *
from gui.results_menu.results_preprocessor import *
from gui.misc.dbf import *
from numpy.random import randint
from database.createDBConnection import createDBC

class QWizardValidatePage(QWizardPage):
    def __init__(self, complete=False, parent=None):
        super(QWizardValidatePage, self).__init__(parent)
        self.complete = complete

    def isComplete(self):
        if self.complete:
            return True
        else:
            return False

class ComboBoxFolder(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFolder, self).__init__(parent)

    def browseFolder(self, index):
        if index  == self.count()-1:
            location = QFileDialog.getExistingDirectory(self, QString("Project Location"), "/home", QFileDialog.ShowDirsOnly)
            if not location.isEmpty():
                indexOfFolder = self.isPresent(location)
                if indexOfFolder is None:
                    self.insertItem(0, QString(location))
                    self.setCurrentIndex(0)
                else:
                    self.setCurrentIndex(indexOfFolder)
            else:
                self.setCurrentIndex(0)

    def isPresent(self, location):
        for i in range(self.count()):
            if location == self.itemText(i):
                return i
        return None

class ComboBoxFile(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFile, self).__init__(parent)

    def browseFile(self, index):
        if index == self.count()-1:
            file = QFileDialog.getOpenFileName(self, QString("Browse to select file"), "/home", "Data Files (*.dat *.txt *.csv)")
            if not file.isEmpty():
                indexOfFile = self.isPresent(file)
                if indexOfFile is None:
                    self.insertItem(1, QString(file))
                    self.setCurrentIndex(1)
                else:
                    self.setCurrentIndex(indexOfFile)
            else:
                self.setCurrentIndex(0)

    def isPresent(self, file):
        for i in range(self.count()):
            if file == self.itemText(i):
                return i
        return None

    def findAndSet(self, text):
        for i in range(self.count()):
            if self.itemText(i) == ('%s' %text):
                self.setCurrentIndex(i)
                return True
        else:
            return False


class DisplayLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(DisplayLineEdit, self).__init__(parent)
        self.setEnabled(False)


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def check(self, text):
        text = self.text()
        try:
            if len(text) == 0:
                raise TextError, "Enter a non-empty string"
            if not re.match("[A-Za-z]",text[0]):
                text = text[1:]
                raise TextError, "First character has to be a alphabet"

            for i in text[1:]:
                if not re.match("[A-Za-z_0-9]", i):
                    text.replace(i, '')
                    raise TextError, "Name can only comprise of alphabets and an underscore (_)"
        except TextError, e:
            QMessageBox.information(self, "Warning",
                                    "%s" %e,
                                    QMessageBox.Ok)
            self.setText(text)
            self.selectAll()
            self.setFocus()
        return True

class Separator(QFrame):
    def __init__(self, parent=None):
        super(Separator, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class NameDialog(QDialog):
    def __init__(self,  title, parent=None):
        super(NameDialog, self).__init__(parent)

        self.setMinimumSize(200, 100)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("./images/modifydata.png"))

        nameLabel = QLabel("Name of the table")
        self.nameLineEdit = LineEdit()
        nameLabel.setBuddy(self.nameLineEdit)
        hLayout = QHBoxLayout()
        hLayout.addWidget(nameLabel)
        hLayout.addWidget(self.nameLineEdit)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        copyWarning = QLabel("""<font color = blue>Enter a name for the table</font> """)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hLayout)
        vLayout.addWidget(copyWarning)
        vLayout.addWidget(dialogButtonBox)

        self.setLayout(vLayout)

        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(self.nameLineEdit, SIGNAL("textChanged(const QString&)"), self.checkName)

    def checkName(self, text):
        try:
            self.nameLineEdit.check(text)
            self.check = True
        except TextError, e:
            QMessageBox.warning(self, "Table Name", "TextError: %s" %e, QMessageBox.Ok)
            self.check = False

    def accept(self):
        if self.check:
            QDialog.accept(self)
        else:
            QMessageBox.warning(self, "Table Name", "Enter a valid table name", QMessageBox.Ok)


class VariableSelectionDialog(QDialog):
    def __init__(self, variableDict, defaultVariables=[], title="", icon="", warning="", parent=None):
        super(VariableSelectionDialog, self).__init__(parent)

        self.defaultVariables = defaultVariables
        self.variableDict = variableDict
        self.variables = self.variableDict.keys()

        self.checkDefaultVariables()

        self.setStatusTip("Dummy String")
        self.setFixedSize(QSize(500,300))

        if len(defaultVariables) == 0:
            dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Reset| QDialogButtonBox.Cancel| QDialogButtonBox.Ok)
        else:
            dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Reset| QDialogButtonBox.RestoreDefaults| QDialogButtonBox.Cancel| QDialogButtonBox.Ok)
        layout = QVBoxLayout()

        selectButton = QPushButton('Select>>')
        unselectButton = QPushButton('<<Deselect')
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(selectButton)
        buttonLayout.addWidget(unselectButton)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("./images/%s.png"%(icon)))

        self.oriVariables = self.variables

        self.variableListWidget = ListWidget(self.variables)
        self.variableListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selectedVariableListWidget = ListWidget([])
        self.selectedVariableListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.variableDescLabel = QLabel("Description of the variables")
        warning = QLabel("<font color = blue>%s</font>" %warning)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.variableListWidget)
        hLayout.addLayout(buttonLayout)
        hLayout.addWidget(self.selectedVariableListWidget)

        layout.addLayout(hLayout)
        layout.addWidget(self.variableDescLabel)
        layout.addWidget(warning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)

        self.variableListWidget.populate()


        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(dialogButtonBox, SIGNAL("clicked(QAbstractButton *)"), self.resetandrestore)
        self.connect(selectButton, SIGNAL("clicked()"), self.moveSelected)
        self.connect(unselectButton, SIGNAL("clicked()"), self.moveUnselected)
        self.connect(self.variableListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.moveSelected)
        self.connect(self.variableListWidget, SIGNAL("currentRowChanged(int)"), self.displayVariableDescription)
        self.connect(self.selectedVariableListWidget, SIGNAL("currentRowChanged(int)"), self.displaySelectedVariableDescription)


    def accept(self):

        QDialog.accept(self)




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

    def moveUnselected(self):
        unselectedItems = self.selectedVariableListWidget.selectedItems()
        for i in unselectedItems:
            self.selectedVariableListWidget.variables.remove(i.text())
            self.variableListWidget.variables.append(i.text())

        self.variableListWidget.populate()
        self.selectedVariableListWidget.populate()

class ListWidget(QListWidget):
    def __init__(self, variables=None, parent=None):
        super(ListWidget, self).__init__(parent)
        self.variables = variables

    def populate(self):
        self.clear()
        if len(self.variables) > 0:
            self.addItems(self.variables)

        self.sortItems()

    def remove(self):
        self.takeItem(self.currentRow())

    def removeList(self, items):
        for i in items:
            self.setItemSelected(i, True)
            self.remove()

    def addList(self, items):
        for i in items:
            self.addItem(i.text())

    def rowOf(self, text):
        for i in range(self.count()):
            if self.item(i).text() == text:
                return i
        return -1

class RecodeDialog(QDialog):
    def __init__(self, project, tablename, title="", icon="", parent=None):
        super(RecodeDialog, self).__init__(parent)

        self.icon = icon

        self.setWindowTitle(title + ' - %s' %tablename)
        self.setWindowIcon(QIcon("./images/%s.png" %icon))

        self.tablename = tablename
        self.variableDict = {}
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.setWindowTitle(title)

        self.setFixedSize(QSize(500, 300))
        self.setWindowTitle(title)

        self.variables = self.variablesInTable()

        self.variableList = QListWidget()

        self.populate()

        oldLabel = QLabel("Variable name to be recoded:")
        self.variableOldEdit = QLineEdit()
        self.variableOldEdit.setEnabled(False)
        newLabel = QLabel("New variable name after recoding:")
        self.variableNewEdit = QLineEdit()
        self.variableNewEdit.setEnabled(False)

        self.oldNewButton = QPushButton("Old and New Values")
        self.oldNewButton.setEnabled(False)

        recodeWarning = QLabel("""<font color = blue>Note: Select the variable whose categories will be """
                               """transformed by double-clicking on the variable. """
                               """ Enter a new variable name for the variable that will contain the transformed categories """
                               """in the <b>New variable name after recoding:</b> line edit box. Then click on """
                               """<b>Old and New Values </b> to define the transformations.</font>""")

        recodeWarning.setWordWrap(True)
        vlayout1 = QVBoxLayout()
        vlayout1.addWidget(self.variableList)

        vlayout2 = QVBoxLayout()
        vlayout2.addWidget(oldLabel)
        vlayout2.addWidget(self.variableOldEdit)
        vlayout2.addWidget(newLabel)
        vlayout2.addWidget(self.variableNewEdit)
        vlayout2.addItem(QSpacerItem(10, 200))
        vlayout2.addWidget(self.oldNewButton)

        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayout1)
        hlayout.addLayout(vlayout2)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addWidget(recodeWarning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)

        self.connect(self.variableList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.moveSelectedVar)
        self.connect(self.variableNewEdit, SIGNAL("textChanged(const QString&)"), self.checkNewVarName)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(self.oldNewButton, SIGNAL("clicked()"), self.relationOldNew)

    def checkNewVarName(self, name):

        import copy
        variables = copy.deepcopy(self.variables)

        variables = [('%s'%i).lower() for i in variables]

        name = ('%s'%name).lower()

        try:
            variables.index(name)
            self.oldNewButton.setEnabled(False)
        except:
            if len(name)>0:
                if not re.match("[A-Za-z]",name[0]):
                    self.oldNewButton.setEnabled(False)
                else:
                    self.oldNewButton.setEnabled(True)
                    if len(name)>1:
                        for i in name[1:]:
                            if not re.match("[A-Za-z_0-9]", i):
                                self.oldNewButton.setEnabled(False)
                            else:
                                self.oldNewButton.setEnabled(True)
            else:
                self.oldNewButton.setEnabled(False)

    def relationOldNew(self):
        variablename = self.variableOldEdit.text()
        varcats = self.variableDict['%s' %variablename]
        newvariablename = self.variableNewEdit.text()


        dia = OldNewRelation(variablename, varcats, icon = self.icon)
        if dia.exec_():
            self.variables.append(newvariablename)
            self.runRecodeCrit(variablename, newvariablename, dia.recodeCrit)
            self.resetDialog()

    def runRecodeCrit(self, variablename, newvariablename, recodeCrit):
        query = QSqlQuery(self.projectDBC.dbc)

        self.addColumn(newvariablename)

        for crit in recodeCrit:
            if not query.exec_("""update %s set %s = %s where %s = %s"""
                               %(self.tablename,
                                 newvariablename,
                                 crit[1],
                                 variablename,
                                 crit[0])):
                raise FileError, query.lastError().text()


    def addColumn(self, variablename):
        query = QSqlQuery(self.projectDBC.dbc)


        if not query.exec_("""alter table %s add column %s text""" %(self.tablename, variablename)):
            raise FileError, query.lastError().text()

    def resetDialog(self):
        self.variableNewEdit.clear()
        self.variableOldEdit.clear()
        self.variableList.clear()
        self.populate()




    def populate(self):
        self.variableList.clear()
        self.variableList.addItems(self.variables)


    def moveSelectedVar(self, listItem):
        self.variableOldEdit.clear()
        varname = listItem.text()
        self.variableOldEdit.setText(varname)
        varCats = self.categories(varname)
        self.variableDict['%s' %varname] = varCats
        self.variableNewEdit.setEnabled(True)

    def variablesInTable(self):
        variables = []
        query = QSqlQuery(self.projectDBC.dbc)
        if not query.exec_("""desc %s""" %self.tablename):
            raise FileError, query.lastError().text()

        FIELD = 0

        while query.next():
            field = query.value(FIELD).toString()
            variables.append(field)

        return variables



    def categories(self, varname):
        cats = []

        query = QSqlQuery(self.projectDBC.dbc)
        if not query.exec_("""select %s from %s group by %s""" %(varname, self.tablename, varname)):
            raise FileError, query.lastError().text()

        CATEGORY = 0

        while query.next():
            cat = unicode(query.value(CATEGORY).toString())
            #try:
            #    cat = query.value(CATEGORY).toInt()[0]
            #except:
            #    cat = query.value(CATEGORY).toString()[0]
            cats.append(cat)

        return cats

class OldNewRelation(QDialog):
    def __init__(self, variablename, varcats, icon, parent=None):
        super(OldNewRelation, self).__init__(parent)

        self.setWindowTitle("Old and New Values")
        self.setWindowIcon(QIcon("./images/%s.png" %icon))

        self.variablename = variablename
        self.varcats = varcats
        self.recCritDict = {}

        varCatsLabel = QLabel("Categories in the variable:")
        self.varCatsList = ListWidget()
        self.varCatsList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        newCatLabel = QLabel("Value of the new category:")
        self.newCatEdit = QLineEdit()

        recodeCritLabel = QLabel("Transformation(s)")
        self.recodeCritList = ListWidget()

        self.addRecCrit = QPushButton("Add")
        self.addRecCrit.setEnabled(False)

        self.removeRecCrit = QPushButton("Remove")
        self.removeRecCrit.setEnabled(False)

        self.copyOldCrit = QPushButton("Copy Old Values")
        self.copyOldCrit.setEnabled(False)

        oldnewWarning = QLabel("""<font color = blue>Note: Highlight the old category from the <b>Categories in the variable</b>"""
                               """ list box and enter a new category value in the <b>Value of the new category</b> """
                               """ line edit box. Click on <b>Add</b> to add a transformation, <b>Remove</b> """
                               """to remove a transformation and <b>Copy Old Values</b> to copy old categories.</font>""")
        oldnewWarning.setWordWrap(True)

        vLayout2 = self.vLayout([varCatsLabel, self.varCatsList, newCatLabel, self.newCatEdit])

        vLayout3 = self.vLayout([self.addRecCrit, self.removeRecCrit, self.copyOldCrit])
        vLayout3.addItem(QSpacerItem(10,100))

        vLayout4 = self.vLayout([recodeCritLabel, self.recodeCritList])


        hLayout = self.hLayout([vLayout2, vLayout3, vLayout4])

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Reset| QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(oldnewWarning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)

        self.populate()

        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(dialogButtonBox, SIGNAL("clicked(QAbstractButton *)"), self.reset)
        self.connect(self.varCatsList, SIGNAL("itemSelectionChanged()"), self.enableAddCrit)
        self.connect(self.varCatsList, SIGNAL("itemSelectionChanged()"), self.enableCopyOldCrit)
        self.connect(self.newCatEdit, SIGNAL("textChanged(const QString&)"), self.enableAddCrit)
        self.connect(self.recodeCritList, SIGNAL("itemSelectionChanged()"), self.enableRemoveCrit)

        self.connect(self.addRecCrit, SIGNAL("clicked()"), self.addRecCritList)
        self.connect(self.removeRecCrit, SIGNAL("clicked()"), self.removeRecCritList)
        self.connect(self.copyOldCrit, SIGNAL("clicked()"), self.addCopyOldCritList)


    def accept(self):
        self.recodeCrit = []

        if not self.recodeCritList.count() < 1:
            for i in range(self.recodeCritList.count()):
                itemText = self.recodeCritList.item(i).text()
                old, new = self.parse(itemText)

                self.recodeCrit.append([old,new])
                QDialog.accept(self)
        else:
            reply = QMessageBox.question(self, "PopGen: Display and Modify Data",
                                         QString("No recode criterion set. Do you wish to continue?"),
                                         QMessageBox.Yes| QMessageBox.No)
            if reply == QMessageBox.Yes:
                QDialog.accept(self)



    def parse(self, text):
        parsed = text.split(',')
        return int(parsed[0]), int(parsed[1])


    def reset(self):
        pass

    def enableAddCrit(self):
        try:
            int(self.newCatEdit.text())
            if len(self.varCatsList.selectedItems())>0:
                self.addRecCrit.setEnabled(True)
            else:
                self.addRecCrit.setEnabled(False)
        except Exception, e:
            self.addRecCrit.setEnabled(False)

    def enableCopyOldCrit(self):
        if len(self.varCatsList.selectedItems())>0:
            self.copyOldCrit.setEnabled(True)
        else:
            self.copyOldCrit.setEnabled(False)



    def enableRemoveCrit(self):
        if len(self.recodeCritList.selectedItems())>0:
            self.removeRecCrit.setEnabled(True)
        else:
            self.removeRecCrit.setEnabled(False)


    def addCopyOldCritList(self):
        items = self.varCatsList.selectedItems()
        recCrit = []

        for i in items:
            crit = '%s' %i.text() + ',' + '%s' %i.text()
            recCrit.append(crit)
            self.recCritDict[crit] = i.text()

        self.recodeCritList.addItems(recCrit)
        self.recodeCritList.sortItems()
        self.varCatsList.removeList(items)
        self.newCatEdit.clear()


    def addRecCritList(self):
        items = self.varCatsList.selectedItems()
        recCrit = []

        newCat = int(self.newCatEdit.text())

        for i in items:
            crit = '%s' %i.text() + ',' + '%s' %newCat
            recCrit.append(crit)
            self.recCritDict[crit] = i.text()

        self.recodeCritList.addItems(recCrit)
        self.recodeCritList.sortItems()
        self.varCatsList.removeList(items)
        self.newCatEdit.clear()


    def removeRecCritList(self):
        items = self.recodeCritList.selectedItems()

        for i in items:
            self.varCatsList.addItem(self.recCritDict['%s' %i.text()])
        self.varCatsList.sortItems()

        self.recodeCritList.removeList(items)


    def populate(self):

        catString = ['%s' %i for i in self.varcats]
        self.varCatsList.addItems(catString)
        self.varCatsList.sortItems()

    def hLayout(self, widgetList):
        layout = QHBoxLayout()
        for i in widgetList:
            layout.addLayout(i)
        return layout

    def vLayout(self, widgetList):
        layout = QVBoxLayout()
        for i in widgetList:
            layout.addWidget(i)
        return layout


class CreateVariable(QDialog):
    def __init__(self, project, tablename, variableTypeDict, title="", icon="", parent=None):
        super(CreateVariable, self).__init__(parent)

        self.setWindowTitle(title + " - %s" %tablename)
        self.setWindowIcon(QIcon("./images/%s.png" %icon))
        self.tablename = tablename
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.variableDict = {}
        self.variables = variableTypeDict.keys()

        newVarLabel = QLabel("New Variable Name")
        self.newVarNameEdit = QLineEdit()
        variableListLabel = QLabel("Variables in Table")
        self.variableListWidget = ListWidget()
        variableCatsListLabel = QLabel("Categories")
        self.variableCatsListWidget = ListWidget()

        formulaLabel = QLabel("Expression")
        self.formulaEdit = QPlainTextEdit()
        formulaEgLabel = QLabel("<font color = brown>Eg. Var1 + Var2 or 11 </font>")
        self.formulaEdit.setEnabled(False)
        whereLabel = QLabel("Filter Expression")
        self.whereEdit = QPlainTextEdit()
        dummy = "Eg. Var1 > 10"
        whereEgLabel = QLabel("<font color = brown>%s</font>" %dummy)
        self.whereEdit.setEnabled(False)

        createVarWarning = QLabel("""<font color = blue>Note: Enter the name of the new variable in <b>New Variable Name</b> """
                                  """line edit box, type the mathematical expression that defines the new variable in the """
                                  """<b>Expression</b> text edit box, and add any mathematical filter expression in the """
                                  """<b>Filter Expression</b> text edit box to create a new variable. """
                                  """The dialog also allows users to check the """
                                  """categories under any variable by clicking the variable in the """
                                  """<b>Variables in Table</b> list box.</font>""")

        createVarWarning.setWordWrap(True)
        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(newVarLabel)
        vLayout2.addWidget(self.newVarNameEdit)

        hLayout1 = QHBoxLayout()
        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(variableListLabel)
        vLayout3.addWidget(self.variableListWidget)
        vLayout4 = QVBoxLayout()
        vLayout4.addWidget(variableCatsListLabel)
        vLayout4.addWidget(self.variableCatsListWidget)
        hLayout1.addLayout(vLayout3)
        hLayout1.addLayout(vLayout4)
        vLayout2.addLayout(hLayout1)

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(formulaLabel)
        vLayout1.addWidget(formulaEgLabel)
        vLayout1.addWidget(self.formulaEdit)

        vLayout1.addWidget(whereLabel)
        vLayout1.addWidget(whereEgLabel)
        vLayout1.addWidget(self.whereEdit)


        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout2)
        hLayout.addLayout(vLayout1)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(createVarWarning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)
        self.populate()

        self.connect(self.newVarNameEdit, SIGNAL("textChanged(const QString&)"), self.checkNewVarName)
        self.connect(self.variableListWidget, SIGNAL("itemSelectionChanged()"), self.displayCats)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))


    def displayCats(self):
        varname = self.variableListWidget.currentItem().text()
        varCats = self.categories(varname)
        self.variableDict['%s' %varname] = varCats

        cats = ['%s' %i for i in self.variableDict['%s' %varname]]

        self.variableCatsListWidget.clear()
        self.variableCatsListWidget.addItems(cats)


    def checkNewVarName(self, name):

        import copy
        variables = copy.deepcopy(self.variables)

        variables = [('%s'%i).lower() for i in variables]

        name = ('%s'%name).lower()

        try:
            variables.index(name)
            self.enable(False)
        except:
            if len(name)>0:
                if not re.match("[A-Za-z]",name[0]):
                    self.enable(False)
                else:
                    self.enable(True)
                    if len(name)>1:
                        for i in name[1:]:
                            if not re.match("[A-Za-z_0-9]", i):
                                self.enable(False)
                            else:
                                self.enable(True)
            else:
                self.enable(False)


    def enable(self, value):
        self.formulaEdit.setEnabled(value)
        self.whereEdit.setEnabled(value)

    def populate(self):
        self.variableListWidget.addItems(self.variables)


    def categories(self, varname):
        cats = []

        query = QSqlQuery(self.projectDBC.dbc)
        query.exec_("""select %s from %s group by %s""" %(varname, self.tablename, varname))

        CATEGORY = 0

        while query.next():
            cat = unicode(query.value(CATEGORY).toString())
            #try:
            #    cat = query.value(CATEGORY).toInt()[0]
            #except:
            #    cat = query.value(CATEGORY).toString()
            #    print cat
            cats.append(cat)


        return cats



class DeleteRows(QDialog):
    def __init__(self, project, tablename, variableTypeDict, title="", icon="", parent=None):
        super(DeleteRows, self).__init__(parent)

        self.setWindowTitle(title + " - %s" %tablename)
        self.setWindowIcon(QIcon("./images/%s.png" %icon))
        self.tablename = tablename
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.variableDict = {}
        self.variables = variableTypeDict.keys()

        variableListLabel = QLabel("Variables in Table")
        self.variableListWidget = ListWidget()
        variableCatsListLabel = QLabel("Categories")
        self.variableCatsListWidget = ListWidget()

        dummy = "Eg. Var1 > 10"
        whereLabel = QLabel("Filter Expression    " + "<font color = brown>%s</font>" %dummy)
        self.whereEdit = QPlainTextEdit()

        createVarWarning = QLabel("""<font color = blue>Note: Enter a mathematical filter expression in the """
                                  """<b>Filter Expression</b> text edit box to delete rows. """
                                  """The dialog also allows users to check the """
                                  """categories under any variable by selecting the variable in the """
                                  """<b>Variables in Table</b> list box.</font>""")

        createVarWarning.setWordWrap(True)
        vLayout2 = QVBoxLayout()

        hLayout1 = QHBoxLayout()
        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(variableListLabel)
        vLayout3.addWidget(self.variableListWidget)
        vLayout4 = QVBoxLayout()
        vLayout4.addWidget(variableCatsListLabel)
        vLayout4.addWidget(self.variableCatsListWidget)
        hLayout1.addLayout(vLayout3)
        hLayout1.addLayout(vLayout4)
        vLayout2.addLayout(hLayout1)

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(whereLabel)
        vLayout1.addWidget(self.whereEdit)


        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout2)
        hLayout.addLayout(vLayout1)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(createVarWarning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)
        self.populate()

        self.connect(self.variableListWidget, SIGNAL("itemSelectionChanged()"), self.displayCats)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))


    def displayCats(self):
        varname = self.variableListWidget.currentItem().text()
        varCats = self.categories(varname)
        self.variableDict['%s' %varname] = varCats

        cats = ['%s' %i for i in self.variableDict['%s' %varname]]

        self.variableCatsListWidget.clear()
        self.variableCatsListWidget.addItems(cats)



    def populate(self):
        self.variableListWidget.addItems(self.variables)


    def categories(self, varname):
        cats = []

        query = QSqlQuery(self.projectDBC.dbc)
        query.exec_("""select %s from %s group by %s""" %(varname, self.tablename, varname))

        CATEGORY = 0

        while query.next():
            cat = unicode(query.value(CATEGORY).toString())
            cats.append(cat)
        return cats

class DisplayMapsDlg(QDialog):
    def __init__(self, project, tablename, title="", icon="", parent=None):
        super(DisplayMapsDlg, self).__init__(parent)

        self.setMinimumSize(QSize(950, 500))

        self.setWindowTitle(title + " - %s" %tablename)
        self.setWindowIcon(QIcon("./images/%s.png" %icon))
        self.tablename = tablename
        self.project = project
        
        check = self.isValid()
        
        if check:
            self.emit(SIGNAL("rejected()"))
            

        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.query = QSqlQuery(self.projectDBC.dbc)
        self.variableDict = {}
        self.variableTypeDict = self.populateVariableTypeDictionary(self.tablename)
        self.variables = self.variableTypeDict.keys()

        variableListLabel = QLabel("Variables in Table")
        self.variableListWidget = ListWidget()
        variableCatsListLabel = QLabel("Categories")
        self.variableCatsListWidget = ListWidget()
        self.variableListWidget.setMaximumWidth(200)
        self.variableCatsListWidget.setMaximumWidth(100)

        # Displaying the thematic map
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(255,255,255))
        self.canvas.enableAntiAliasing(True)
        self.canvas.useQImageToRender(False)

        if self.project.resolution == "County":
            self.res_prefix = "co"
        if self.project.resolution == "Tract":
            self.res_prefix = "tr"
        if self.project.resolution == "Blockgroup":
            self.res_prefix = "bg"

        self.stateCode = self.project.stateCode[self.project.state]
        resultfilename = self.res_prefix+self.stateCode+"_selected"
        self.resultsloc = self.project.location + os.path.sep + self.project.name + os.path.sep + "results"
        
        self.resultfileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".shp")
        self.dbffileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".dbf")

        layerName = self.project.name + '-' + self.project.resolution
        layerProvider = "ogr"
        self.layer = QgsVectorLayer(self.resultfileloc, layerName, layerProvider)

        renderer = self.layer.renderer()
        renderer.setSelectionColor(QColor(255,255,0))

        symbol = renderer.symbols()[0]
        symbol.setFillColor(QColor(153,204,0))

        if not self.layer.isValid():
            return
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.canvas.setExtent(self.layer.extent())
        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        #self.canvas.setLayerSet(layers)

        self.toolbar = Toolbar(self.canvas, self.layer)
        self.toolbar.hideDragTool()
        self.toolbar.hideSelectTool()
        

        mapLabel = QLabel("Thematic Map")

        



        createVarWarning = QLabel("""<font color = blue>Note: Enter a mathematical filter expression in the """
                                  """<b>Filter Expression</b> text edit box to delete rows. """
                                  """The dialog also allows users to check the """
                                  """categories under any variable by selecting the variable in the """
                                  """<b>Variables in Table</b> list box.</font>""")

        createVarWarning.setWordWrap(True)
        vLayout2 = QVBoxLayout()

        hLayout1 = QHBoxLayout()
        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(variableListLabel)
        vLayout3.addWidget(self.variableListWidget)
        vLayout4 = QVBoxLayout()
        vLayout4.addWidget(variableCatsListLabel)
        vLayout4.addWidget(self.variableCatsListWidget)
        hLayout1.addLayout(vLayout3)
        hLayout1.addLayout(vLayout4)
        vLayout2.addLayout(hLayout1)

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(mapLabel)
        vLayout1.addWidget(self.toolbar)
        vLayout1.addWidget(self.canvas)


        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout2)
        hLayout.addLayout(vLayout1)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addLayout(hLayout)
        layout.addWidget(createVarWarning)
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)
        self.populate()

        self.connect(self.variableListWidget, SIGNAL("itemSelectionChanged()"), self.displayCats)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(self.variableCatsListWidget, SIGNAL("itemSelectionChanged()"), self.displayMap)


    def isValid(self):
        retval = -1
        if not self.isResolutionValid():
            retval = 1
            return retval
        elif not self.isLayerValid():
            retval = 2
            return retval
        elif not self.isPopSyn():
            retval = 3
            return retval
        else:
            return retval

    def isResolutionValid(self):
        return self.project.resolution != "TAZ"

    def isLayerValid(self):
        res = ResultsGen(self.project)
        return res.create_hhmap()

    def isPopSyn(self):
        self.getGeographies()
        return len(self.geolist)>0

    def getGeographies(self):
        self.geolist = []
        for geo in self.project.synGeoIds.keys():
            geostr = str(geo[0]) + "," + str(geo[1]) + "," + str(geo[3]) + "," + str(geo[4])
            self.geolist.append(geostr)


    def accept(self):
        self.projectDBC.dbc.close()
        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)



    def makeTempTables(self):
        varstr = self.variableListWidget.currentItem().text()
        varcatstr = self.variableCatsListWidget.currentItem().text()

        if self.tablename == 'hhld_sample':
            fromTable = 'housing_synthetic_data'
            toTable = 'temphhld'

        if self.tablename == 'gq_sample':
            fromTable = 'housing_synthetic_data'
            toTable = 'tempgq'
        else:
            fromTable = 'person_synthetic_data'
            toTable = 'temp'

        query = QSqlQuery(self.projectDBC.dbc)
        query.exec_(""" DROP TABLE IF EXISTS %s""" %(toTable))
        if not query.exec_("""CREATE TABLE %s SELECT %s.*,%s FROM %s"""
                            """ LEFT JOIN %s using (serialno)""" %(toTable, fromTable, varstr, fromTable, self.tablename)):
            raise FileError, query.lastError().text()
        if not query.exec_("""select state, county, tract, bg, sum(frequency) from %s where %s = %s """
                           """group by state, county, tract, bg"""
                           %(toTable, varstr, varcatstr)):
            raise FileError, query.lastError().text()

        distDict = {}

        while query.next():
            state = str(query.value(0).toString())
            county = str(query.value(1).toString())
            tract = str(query.value(2).toString())
            bg = str(query.value(3).toString())

            value = query.value(4).toInt()[0]

            key = (state, county, tract, bg)
            
            distDict[key] = value

        return distDict


    def displayMap(self):

        distDict = self.makeTempTables()
        print distDict


        self.stateCode = self.project.stateCode[self.project.state]
        resultfilename = self.res_prefix+self.stateCode+"_selected"
        self.resultsloc = self.project.location + os.path.sep + self.project.name + os.path.sep + "results"
        
        self.resultfileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".shp")
        self.dbffileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".dbf")

        layerName = self.project.name + '-' + self.project.resolution
        layerProvider = "ogr"
        self.layer = QgsVectorLayer(self.resultfileloc, layerName, layerProvider)

        # Generating a random number field to the shape files database
        var =  'random1'
        f = open(self.dbffileloc, 'rb')
        db = list(dbfreader(f))
        f.close()
        fieldnames, fieldspecs, records = db[0], db[1], db[2:]
        if var not in fieldnames:
            fieldnames.append(var)
            fieldspecs.append(('N',11,0))
            for rec in records:
                rec.append(randint(0,100))
            f = open(self.dbffileloc, 'wb')
            dbfwriter(f, fieldnames, fieldspecs, records)
            f.close()



        self.layer.setRenderer(QgsContinuousColorRenderer(self.layer.vectorType()))
        r = self.layer.renderer()
        provider = self.layer.getDataProvider()
        idx = provider.indexFromFieldName(var)

        r.setClassificationField(idx)
        min = provider.minValue(idx).toString()
        max = provider.maxValue(idx).toString()
        minsymbol = QgsSymbol(self.layer.vectorType(), min, "","")
        minsymbol.setBrush(QBrush(QColor(255,255,255)))
        maxsymbol = QgsSymbol(self.layer.vectorType(), max, "","")
        maxsymbol.setBrush(QBrush(QColor(0,0,0)))
        r.setMinimumSymbol(minsymbol)
        r.setMaximumSymbol(maxsymbol)
        r.setSelectionColor(QColor(255,255,0))

        QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.canvas.setExtent(self.layer.extent())

        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        self.canvas.setLayerSet(layers)

        self.canvas.refresh()






    def populateVariableTypeDictionary(self, tablename):

        variableTypeDictionary = {}
        self.query.exec_("""desc %s""" %tablename)

        FIELD, TYPE, NULL, KEY, DEFAULT, EXTRA = range(6)

        while self.query.next():
            field = '%s' %self.query.value(FIELD).toString()
            type = self.query.value(TYPE).toString()
            null = self.query.value(NULL).toString()
            key = self.query.value(KEY).toString()
            default = self.query.value(DEFAULT).toString()
            extra = self.query.value(EXTRA).toString()

            if not field in ['state', 'pumano', 'hhid', 'serialno', 'pnum']:
                variableTypeDictionary['%s' %field] = type

        return variableTypeDictionary


    def displayCats(self):
        varname = self.variableListWidget.currentItem().text()
        varCats = self.categories(varname)
        self.variableDict['%s' %varname] = varCats

        cats = ['%s' %i for i in self.variableDict['%s' %varname]]

        self.variableCatsListWidget.clear()
        self.variableCatsListWidget.addItems(cats)



    def populate(self):
        self.variableListWidget.addItems(self.variables)


    def categories(self, varname):
        cats = []

        self.query.exec_("""select %s from %s group by %s""" %(varname, self.tablename, varname))

        CATEGORY = 0

        while self.query.next():
            cat = unicode(self.query.value(CATEGORY).toString())
            cats.append(cat)
        return cats



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    var = {}
    var['first'] = [1,2,3,4,-99]
    var['second'] = [3,4,1,-1]

    dia = CreateVariable(var)
    dia.show()
    app.exec_()


