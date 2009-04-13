from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from database.createDBConnection import createDBC
from file_menu.newproject import DBInfo
from misc.widgets import *
from misc.errors import *

class DisplayTable(QDialog):
    def __init__(self, tablename, parent=None):
        super(DisplayTable, self).__init__(parent)
        self.tablename = tablename

        self.setWindowTitle("Data Table - %s" %self.tablename)

        self.populateVariableDictionary()

        self.model = QSqlTableModel()
        self.model.setTable(self.tablename)
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setMinimumSize(QSize(800, 500))
        self.output = QTextEdit()
        self.output.setMinimumSize(QSize(800, 100))

        layoutView = QVBoxLayout()
        layoutView.addWidget(self.view)
        layoutView.addWidget(self.output)

        descButton = QPushButton("Decriptives")
        freqButton = QPushButton("Frequencies")
        modifyDefButton = QPushButton("Modify Definition")
        modifyButton = QPushButton("Modify Categories")
        createButton = QPushButton("Create Variable")
        defaultButton = QPushButton("Default Transformations")

        layoutButton = QVBoxLayout()
        layoutButton.addItem(QSpacerItem(10, 175))
        layoutButton.addWidget(descButton)
        layoutButton.addWidget(freqButton)
        layoutButton.addWidget(modifyDefButton)
        layoutButton.addWidget(modifyButton)
        layoutButton.addWidget(createButton)
        layoutButton.addWidget(defaultButton)
        layoutButton.addItem(QSpacerItem(10, 175))

        hLayout = QHBoxLayout()
        hLayout.addLayout(layoutView)
        hLayout.addLayout(layoutButton)



        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hLayout)
        vLayout.addWidget(buttonBox)

        self.setLayout(vLayout)

        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        
        self.connect(descButton, SIGNAL("clicked()"), self.descriptives)
        self.connect(freqButton, SIGNAL("clicked()"), self.frequencies)
        self.connect(modifyDefButton, SIGNAL("clicked()"), self.modifyDefinition)
        self.connect(modifyButton, SIGNAL("clicked()"), self.modifyCategories)
        self.connect(createButton, SIGNAL("clicked()"), self.createVariable)
        self.connect(defaultButton, SIGNAL("clicked()"), self.default)
        
    def descriptives(self):
        descriptivesVarDialog = VariableSelectionDialog(self.variableTypeDictionary, 
                                                        title = "Descriptives")
        if descriptivesVarDialog.exec_():
            self.descriptivesVariablesSelected = descriptivesVarDialog.selectedVariableListWidget.variables
            

            COUNT, AVERAGE, MINIMUM, MAXIMUM, SUM = range(5)
            
            query = QSqlQuery()

            self.output.append("DESCRIPTIVES:")
            self.output.append("%s, %s, %s, %s, %s, %s" %('FIELD', 'COUNT', 'AVERAGE', 'MINIMUM', 'MAXIMUM', 'SUM'))

            for i in self.descriptivesVariablesSelected:

                if not query.exec_("""select count(%s), avg(%s), min(%s), max(%s), sum(%s) from %s"""
                               %(i, i, i, i, i, self.tablename)):
                    raise FileError, query.lastError().text()
                while query.next():
                    count = query.value(COUNT).toInt()[0]
                    average = query.value(AVERAGE).toDouble()[0]
                    minimum = query.value(MINIMUM).toInt()[0]
                    maximum = query.value(MAXIMUM).toInt()[0]
                    sum = query.value(SUM).toInt()[0]
                self.output.append("%s, %s, %s, %s, %s, %s" %(i, count, average, minimum, maximum, sum))
            self.output.append("")
            
    
    def frequencies(self):
        frequenciesVarDialog = VariableSelectionDialog(self.variableTypeDictionary, 
                                                        title = "Descriptives")
        if frequenciesVarDialog.exec_():
            self.frequenciesVariablesSelected = frequenciesVarDialog.selectedVariableListWidget.variables

            CATEGORY, FREQUENCY = range(2)
            
            query = QSqlQuery()

            self.output.append("FREQUENCIES:")

            for i in self.frequenciesVariablesSelected:
                self.output.append("Variable Name - %s" %i)
                self.output.append("%s, %s" %('CATEGORY', 'FREQUENCY'))
            
                if not query.exec_("""select %s, count(*) from %s group by %s"""
                               %(i, self.tablename, i)):
                    raise FileError, query.lastError().text()
                while query.next():
                    category = query.value(CATEGORY).toString()
                    frequency = query.value(FREQUENCY).toInt()[0]
                    self.output.append("%s, %s" %(category, frequency))
                self.output.append("The %s variable has a total of %s categories" %(i, query.size()))
                self.output.append("")
            
    
    def modifyDefinition(self):
        print "Modify Variable Definition"
        pass

    def modifyCategories(self):
        modify = RecodeDialog(self.tablename, self.variableTypeDictionary, title = "Recode Categories")

        
        if modify.exec_():
            pass


    def createVariable(self):
        print "Create variable"
        pass

    def default(self):
        print "Transformations to default categories"


    def populateVariableDictionary(self):
        query = QSqlQuery()
        query.exec_("""desc %s""" %self.tablename)

        FIELD, TYPE, NULL, KEY, DEFAULT, EXTRA = range(6)

        self.variableTypeDictionary = {}

        while query.next():
            field = query.value(FIELD).toString()
            type = query.value(TYPE).toString()
            null = query.value(NULL).toString()
            key = query.value(KEY).toString()
            default = query.value(DEFAULT).toString()
            extra = query.value(EXTRA).toString()
            
            self.variableTypeDictionary['%s' %field] = type
            

class ModifyData(QDialog):
    def __init__(self, parent=None):
        super(ModifyData, self).__init__(parent)
        
        self.setFixedSize(900, 600)
        self.setTitle("Modify table %s" %(tablename))

        self.ediLabel = QLabel("Enter your SQL modifying commands here")
        self.commandTextEdit = QTextEdit()

        #self.dialogButtonBox = QDialogButtonBox( 


