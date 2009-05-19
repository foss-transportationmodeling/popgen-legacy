from PyQt4.QtCore import *
from PyQt4.QtGui import *
from misc.widgets import *



class ControlDataPage(QWizardPage):
    def __init__(self, parent=None):
        super(ControlDataPage, self).__init__(parent)

        self.controlHHLocationDummy = True
        self.controlPersonLocationDummy = True
        
        self.setTitle("Step 4: Control Totals")

        self.controlGroupBox = QGroupBox("""Do you wish to provide the marginal totals for """
                                         """population characteristics of interest?""")
        self.controlUserProvRadio = QRadioButton("Yes")
        self.controlAutoRadio = QRadioButton("No")
        self.controlAutoRadio.setChecked(True)
        controlHLayout = QHBoxLayout()
        controlHLayout.addWidget(self.controlUserProvRadio)
        controlHLayout.addWidget(self.controlAutoRadio)
        self.controlGroupBox.setLayout(controlHLayout)

        controlHHLocationLabel = QLabel("Select the household control file")
        controlGQLocationLabel = QLabel("Select the groupquarter control file")
        controlPersonLocationLabel = QLabel("Select the population control file")

        self.controlHHLocationComboBox = ComboBoxFile()
        self.controlHHLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        controlHHLocationLabel.setBuddy(self.controlHHLocationComboBox)

        self.controlGQLocationComboBox = ComboBoxFile()
        self.controlGQLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        controlGQLocationLabel.setBuddy(self.controlGQLocationComboBox)

        self.controlPersonLocationComboBox = ComboBoxFile()
        self.controlPersonLocationComboBox.addItems([QString(""), QString("Browse to select file...")])
        controlPersonLocationLabel.setBuddy(self.controlPersonLocationComboBox)

        self.controlUserProvGroupBox = QGroupBox("User provided:")
        controlVLayout = QVBoxLayout()
        controlVLayout.addWidget(controlHHLocationLabel)
        controlVLayout.addWidget(self.controlHHLocationComboBox)
        controlVLayout.addWidget(controlGQLocationLabel)
        controlVLayout.addWidget(self.controlGQLocationComboBox)
        controlVLayout.addWidget(controlPersonLocationLabel)
        controlVLayout.addWidget(self.controlPersonLocationComboBox)
        self.controlUserProvGroupBox.setLayout(controlVLayout)
        self.controlUserProvGroupBox.setEnabled(False)
        
        vLayout = QVBoxLayout()
        vLayout.addWidget(self.controlGroupBox)
        vLayout.addWidget(self.controlUserProvGroupBox)
        self.setLayout(vLayout)

        self.connect(self.controlHHLocationComboBox, SIGNAL("activated(int)"), self.controlHHCheck)
        self.connect(self.controlGQLocationComboBox, SIGNAL("activated(int)"), self.controlGQLocationComboBox.browseFile)
        self.connect(self.controlPersonLocationComboBox, SIGNAL("activated(int)"), self.controlPersonCheck)
        self.connect(self.controlAutoRadio, SIGNAL("clicked()"), self.controlAutoAction)
        self.connect(self.controlUserProvRadio, SIGNAL("clicked()"), self.controlUserProvAction)


    def controlAutoAction(self):
        self.controlUserProvGroupBox.setEnabled(False)
        self.controlHHLocationComboBox.setCurrentIndex(0)
        self.controlGQLocationComboBox.setCurrentIndex(0)
        self.controlPersonLocationComboBox.setCurrentIndex(0)
        self.controlPersonLocationDummy = True
        self.controlHHLocationDummy = True
        self.emit(SIGNAL("completeChanged()"))
    
    def controlUserProvAction(self):
        self.controlUserProvGroupBox.setEnabled(True)
        self.controlHHLocationDummy = 0
        self.controlPersonLocationDummy = 0
        self.emit(SIGNAL("completeChanged()"))


    def controlHHCheck(self, index):
        self.controlHHLocationComboBox.browseFile(index)
        if self.controlHHLocationComboBox.currentIndex() == 0:
            self.controlHHLocationDummy = False
        else:
            self.controlHHLocationDummy = True

        self.emit(SIGNAL("completeChanged()"))

    def controlPersonCheck(self, index):
        self.controlPersonLocationComboBox.browseFile(index)
        if self.controlPersonLocationComboBox.currentIndex() == 0:
            self.controlPersonLocationDummy = False
        else:
            self.controlPersonLocationDummy = True

        self.emit(SIGNAL("completeChanged()"))


    def isComplete(self):
        validate = self.controlHHLocationDummy and self.controlPersonLocationDummy
        if validate:
            return True
        else:
            return False



