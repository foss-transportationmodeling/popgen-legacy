from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from misc.errors import *
from misc.widgets import *


class SampleDataPage(QWizardPage):
    def __init__(self, parent=None):
        super(SampleDataPage, self).__init__(parent)

        self.sampleHHLocationDummy = True
        self.samplePersonLocationDummy = True

        self.setTitle("Step 3: Population Sample")

        self.sampleGroupBox = QGroupBox("""Do you wish to provide sample data or the program will"""
                                         """use PUMS for population synthesis?""")
        self.sampleUserProvRadio = QRadioButton("Yes")
        self.sampleAutoRadio = QRadioButton("No")
        self.sampleAutoRadio.setChecked(True)
        sampleHLayout = QHBoxLayout()
        sampleHLayout.addWidget(self.sampleUserProvRadio)
        sampleHLayout.addWidget(self.sampleAutoRadio)
        self.sampleGroupBox.setLayout(sampleHLayout)

        sampleHHLocationLabel = QLabel("Select the household sample file")
        sampleGQLocationLabel = QLabel("Select the groupquarter sample file")
        samplePersonLocationLabel = QLabel("Select the population sample file")

        self.sampleHHLocationComboBox = ComboBoxFile()
        self.sampleHHLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        sampleHHLocationLabel.setBuddy(self.sampleHHLocationComboBox)

        self.sampleGQLocationComboBox = ComboBoxFile()
        self.sampleGQLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        sampleGQLocationLabel.setBuddy(self.sampleGQLocationComboBox)

        self.samplePersonLocationComboBox = ComboBoxFile()
        self.samplePersonLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        samplePersonLocationLabel.setBuddy(self.samplePersonLocationComboBox)

        self.sampleUserProvGroupBox = QGroupBox("User provided:")
        sampleVLayout = QVBoxLayout()
        sampleVLayout.addWidget(sampleHHLocationLabel)
        sampleVLayout.addWidget(self.sampleHHLocationComboBox)
        sampleVLayout.addWidget(sampleGQLocationLabel)
        sampleVLayout.addWidget(self.sampleGQLocationComboBox)
        sampleVLayout.addWidget(samplePersonLocationLabel)
        sampleVLayout.addWidget(self.samplePersonLocationComboBox)
        self.sampleUserProvGroupBox.setLayout(sampleVLayout)

        self.sampleUserProvGroupBox.setEnabled(False)

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.sampleGroupBox)
        vLayout.addWidget(self.sampleUserProvGroupBox)
        self.setLayout(vLayout)


        self.connect(self.sampleHHLocationComboBox, SIGNAL("activated(int)"), self.sampleHHCheck)
        self.connect(self.sampleGQLocationComboBox, SIGNAL("activated(int)"), self.sampleGQLocationComboBox.browseFile)
        self.connect(self.samplePersonLocationComboBox, SIGNAL("activated(int)"), self.samplePersonCheck)

        self.connect(self.sampleAutoRadio, SIGNAL("clicked()"), self.sampleAutoAction)
        self.connect(self.sampleUserProvRadio, SIGNAL("clicked()"), self.sampleUserProvAction)

    def sampleAutoAction(self):
        self.sampleUserProvGroupBox.setEnabled(False)
        self.sampleHHLocationComboBox.setCurrentIndex(0)
        self.sampleGQLocationComboBox.setCurrentIndex(0)
        self.samplePersonLocationComboBox.setCurrentIndex(0)
        self.sampleHHLocationDummy = True
        self.samplePersonLocationDummy = True
        self.emit(SIGNAL("completeChanged()"))


    def sampleUserProvAction(self):
        self.sampleUserProvGroupBox.setEnabled(True)
        self.sampleHHLocationDummy = 0
        self.samplePersonLocationDummy = 0
        self.emit(SIGNAL("completeChanged()"))


    def sampleHHCheck(self, index):
        self.sampleHHLocationComboBox.browseFile(index)
        if self.sampleHHLocationComboBox.currentIndex() == 0:
            self.sampleHHLocationDummy = False
        else:
            self.sampleHHLocationDummy = True

        self.emit(SIGNAL("completeChanged()"))

    def samplePersonCheck(self, index):
        self.samplePersonLocationComboBox.browseFile(index)
        if self.samplePersonLocationComboBox.currentIndex() == 0:
            self.samplePersonLocationDummy = False
        else:
            self.samplePersonLocationDummy = True

        self.emit(SIGNAL("completeChanged()"))


    def isComplete(self):
        validate = self.sampleHHLocationDummy and self.samplePersonLocationDummy
        if validate:
            return True
        else:
            return False



