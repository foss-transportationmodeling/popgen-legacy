from PyQt4.QtCore import *
from PyQt4.QtGui import *
from misc.widgets import *


class ResolutionPage(QWizardPage):
    def __init__(self, parent=None):
        super(ResolutionPage, self).__init__(parent)

        self.geocorrLocationDummy = True

        self.setTitle("Step 2: Resolution of the Population Synthesis")

        resolutionLabel = QLabel("At what resolution do you want to synthesize the population (County/Tract/Blockgroup level)?")
        self.resolutionComboBox = QComboBox()
        self.resolutionComboBox.addItems([QString("County"), QString("Tract"), QString("Blockgroup"), QString("TAZ")])
        self.resolutionComboBox.setFixedSize(QSize(250,20))
        self.geocorrGroupBox = QGroupBox("Will you provide Geographic Correspondence between the Geography and PUMA?")
        self.geocorrUserProvRadio = QRadioButton("Yes")
        self.geocorrAutoRadio = QRadioButton("No")
        self.geocorrAutoRadio.setChecked(True)
        geocorrHLayout = QHBoxLayout()
        geocorrHLayout.addWidget(self.geocorrUserProvRadio)
        geocorrHLayout.addWidget(self.geocorrAutoRadio)
        self.geocorrGroupBox.setLayout(geocorrHLayout)

        geocorrLocationLabel = QLabel("Select the geographic correspondence file")
        self.geocorrLocationComboBox = ComboBoxFile()
        self.geocorrLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        geocorrLocationLabel.setBuddy(self.geocorrLocationComboBox)

        self.geocorrUserProvGroupBox = QGroupBox("User provided:")
        geocorrVLayout = QVBoxLayout()
        geocorrVLayout.addWidget(geocorrLocationLabel)
        geocorrVLayout.addWidget(self.geocorrLocationComboBox)
        self.geocorrUserProvGroupBox.setLayout(geocorrVLayout)
        self.geocorrUserProvGroupBox.setEnabled(False)
        

        vLayout = QVBoxLayout()
        vLayout.addWidget(resolutionLabel)
        vLayout.addWidget(self.resolutionComboBox)
        vLayout.addWidget(self.geocorrGroupBox)
        vLayout.addWidget(self.geocorrUserProvGroupBox)
        self.setLayout(vLayout)
        
        self.connect(self.geocorrAutoRadio, SIGNAL("clicked()"), self.geocorrAutoAction)
        self.connect(self.geocorrUserProvRadio, SIGNAL("clicked()"), self.geocorrUserProvAction)
        self.connect(self.geocorrLocationComboBox, SIGNAL("activated(int)"), self.fileCheck)
        self.connect(self.resolutionComboBox, SIGNAL("activated(int)"), self.resolutionAction)

    def resolutionAction(self):
        if self.resolutionComboBox.currentText() == 'TAZ':
            self.geocorrUserProvRadio.setChecked(True)
            self.geocorrUserProvRadio.emit(SIGNAL("clicked()"))
            self.geocorrAutoRadio.setEnabled(False)
        else:
            self.geocorrAutoRadio.setEnabled(True)

    def geocorrAutoAction(self):
        self.geocorrUserProvGroupBox.setEnabled(False)
        self.geocorrLocationComboBox.setCurrentIndex(0)
        self.geocorrLocationDummy = True
        self.emit(SIGNAL("completeChanged()"))

    def geocorrUserProvAction(self):
        self.geocorrUserProvGroupBox.setEnabled(True)
        self.geocorrLocationDummy = False
        self.emit(SIGNAL("completeChanged()"))

    def fileCheck(self, index):
        self.geocorrLocationComboBox.browseFile(index)
        if self.geocorrLocationComboBox.currentIndex() == 0:
            self.geocorrLocationDummy = False
        else:
            self.geocorrLocationDummy = True
        self.emit(SIGNAL("completeChanged()"))

    def isComplete(self):
        validate = self.geocorrLocationDummy
        if validate:
            return True
        else:
            return False
