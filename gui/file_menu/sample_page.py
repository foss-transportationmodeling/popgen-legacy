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

        self.sampleGroupBox = QGroupBox("""a. Will you provide sample data?""")
        sampleWarning = QLabel("""<font color = blue>Note: If no is chosen, US Census Public Use """
                               """Microdata Sample for year 2000 will be used. </font>""")
        self.sampleUserProvRadio = QRadioButton("Yes")
        self.sampleAutoRadio = QRadioButton("No")
        self.sampleAutoRadio.setChecked(True)
        sampleHLayout = QHBoxLayout()
        sampleHLayout.addWidget(self.sampleUserProvRadio)
        sampleHLayout.addWidget(self.sampleAutoRadio)
        self.sampleGroupBox.setLayout(sampleHLayout)

        sampleHHLocationLabel = QLabel("Select the Household Sample file")
        sampleGQLocationLabel = QLabel("Select the Groupquarter Sample file")
        samplePersonLocationLabel = QLabel("Select the Population Sample file")

        self.sampleHHLocationComboBox = ComboBoxFile()
        self.sampleHHLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        sampleHHLocationLabel.setBuddy(self.sampleHHLocationComboBox)

        self.sampleGQLocationComboBox = ComboBoxFile()
        self.sampleGQLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        sampleGQLocationLabel.setBuddy(self.sampleGQLocationComboBox)

        self.samplePersonLocationComboBox = ComboBoxFile()
        self.samplePersonLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        samplePersonLocationLabel.setBuddy(self.samplePersonLocationComboBox)

        sampleUserProvWarning = QLabel("""<font color = blue> Note: Groupquarter data is optional but if the person control"""
                                       """ totals include residents of groupquarters then provide groupquarter information as well"""
                                       """ to generate a representative synthetic population. </font>""")
        sampleUserProvWarning.setWordWrap(True)

        self.sampleUserProvGroupBox = QGroupBox("b. User provided")
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
        vLayout.addWidget(sampleWarning)
        vLayout.addWidget(self.sampleUserProvGroupBox)
        vLayout.addWidget(sampleUserProvWarning)
        self.setLayout(vLayout)


        self.connect(self.sampleHHLocationComboBox, SIGNAL("activated(int)"), self.sampleHHCheck)
        self.connect(self.sampleGQLocationComboBox, SIGNAL("activated(int)"), self.sampleGQLocationComboBox.browseFile)
        self.connect(self.samplePersonLocationComboBox, SIGNAL("activated(int)"), self.samplePersonCheck)

        self.connect(self.sampleAutoRadio, SIGNAL("clicked()"), self.sampleAutoAction)
        self.connect(self.sampleUserProvRadio, SIGNAL("clicked()"), self.sampleUserProvAction)
        self.connect(self, SIGNAL("resolutionChanged"), self.resolutionAction)

    def resolutionAction(self, resolution):
        if resolution == 'TAZ':
            self.sampleUserProvRadio.setChecked(True)
            self.sampleUserProvRadio.emit(SIGNAL("clicked()"))
            self.sampleAutoRadio.setEnabled(False)
        else:
            self.sampleAutoRadio.setEnabled(True)

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



