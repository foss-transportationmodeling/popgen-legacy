from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
#from misc.errors import *

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
                    raise TextError, "Project name can only comprise of alphabets and an underscore (_)"
        except TextError, e:
            QMessageBox.information(self, "PopSim: New Project Wizard", 
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


class VariableSelectionDialog(QDialog):
    def __init__(self, variableDict, defaultVariables=[], title="", icon="", parent=None):
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
        self.connect(self.variableListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.moveSelected)
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

    def moveUnselected(self):
        unselectedItems = self.selectedVariableListWidget.selectedItems()
        for i in unselectedItems:
            self.selectedVariableListWidget.variables.remove(i.text())
            self.variableListWidget.variables.append(i.text())

        self.variableListWidget.populate()
        self.selectedVariableListWidget.populate()

class ListWidget(QListWidget):
    def __init__(self, variables=None, parent = None):
        super(ListWidget, self).__init__(parent)
        self.variables = variables

    def populate(self):
        self.clear()
        if len(self.variables) > 0:
            self.addItems(self.variables)

        self.sortItems()

    def remove(self):
        self.takeItem(self.currentRow())


    def rowOf(self, text):
        for i in range(self.count()):
            if self.item(i).text() == text:
                return i
        return -1

class RecodeDialog(QDialog):
    def __init__(self, tablename, variableDict, title="", icon="", parent = None):
        super(RecodeDialog, self).__init__(parent)

        self.tablename = tablename
        self.variableDict = variableDict
        
        self.setFixedSize(QSize(500, 300))
        self.setWindowTitle(title)

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
        layout.addWidget(dialogButtonBox)

        self.setLayout(layout)
        
        self.connect(self.variableList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.moveSelectedVar)
        self.connect(self.variableNewEdit, SIGNAL("textChanged(const QString&)"), self.checkNewVarName)
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.connect(self.oldNewButton, SIGNAL("clicked()"), self.relationOldNew)
        
    def checkNewVarName(self, name):
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
        dia = OldNewRelation(self.tablename, self.variableOldEdit.text())
        dia.exec_()

    def populate(self):
        self.variableList.clear()
        self.variableList.addItems(self.variableDict.keys())


    def moveSelectedVar(self, listItem):
        self.variableOldEdit.clear()
        self.variableOldEdit.setText(listItem.text())
        self.variableNewEdit.setEnabled(True)



    def moveSelected(self):
        pass

class OldNewRelation(QDialog):
    def __init__(self, tablename, variablename, parent=None):
        super(OldNewRelation, self).__init__(parent)

        self.tablename = tablename
        self.variablename = variablename
        
        varCatLabel = QLabel("Categories in the original variable")
        self.variableCatList = QListWidget()

        self.value = QRadioButton("Value")
        self.range = QRadioButton("Range")
        self.LowestThru = QRadioButton("Lowest through value")
        self.valueThru = QRadioButton("Value through highest")
        self.allValues = QRadioButton("All other values")

        self.relationGroupBox = QGroupBox("Relation:")
        vlayout1 = QVBoxLayout()
        vlayout1.addWidget(self.value)
        vlayout1.addWidget(self.range)
        vlayout1.addWidget(self.LowestThru)
        vlayout1.addWidget(self.valueThru)
        vlayout1.addWidget(self.allValues)
        self.relationGroupBox.setLayout(vlayout1)


        self.recodeRelationList = QListWidget()

        layout = QHBoxLayout()
        layout.addWidget(self.relationGroupBox)
        layout.addWidget(self.recodeRelationList)
        
        self.setLayout(layout)

        
