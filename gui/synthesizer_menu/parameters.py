import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from gui.misc.widgets import *





class ParametersDialog(QDialog):
    def __init__(self, project, parent = None):
        super(ParametersDialog, self).__init__(parent)

        self.setWindowTitle("PopSim: Parameters")
        self.setWindowIcon(QIcon("./images/parameters.png"))

        self.project = project

        ipfTolLabel = QLabel("Tolerance level for convergence in the IPF procedure")
        ipfTolEdit = QLineEdit()
        ipfTolLabel.setBuddy(ipfTolEdit)
        ipfTolEdit.setText('%s' %self.project.parameters.ipfTol)
        #ipfTolEdit.setText('%s' %IPF_TOLERANCE)
        
        ipfMaxIterLabel = QLabel("Maximum iterations after which IPF procedure should stop")
        ipfMaxIterEdit = QSpinBox()
        ipfMaxIterLabel.setBuddy(ipfMaxIterEdit)
        ipfMaxIterEdit.setRange(0,  500)
        ipfMaxIterEdit.setValue(self.project.parameters.ipfIter)
        #ipfMaxIterEdit.setValue(IPF_MAX_ITERATIONS)
                           
        ipuTolLabel = QLabel("Tolerance level for convergence in the IPU procedure")
        ipuTolEdit = QLineEdit()
        ipuTolLabel.setBuddy(ipfTolEdit)        
        ipuTolEdit.setText('%s' %self.project.parameters.ipuTol)
        #ipuTolEdit.setText('%s' %IPU_TOLERANCE)
        
        ipuMaxIterLabel = QLabel("Maximum iterations after which IPU procedure should stop")
        ipuMaxIterEdit = QSpinBox()
        ipuMaxIterLabel.setBuddy(ipuMaxIterEdit)
        ipuMaxIterEdit.setRange(0,  500)
        ipuMaxIterEdit.setValue(self.project.parameters.ipuIter)
        #ipuMaxIterEdit.setValue(IPU_MAX_ITERATIONS)
        
        synPopDrawsLabel = QLabel("Maximum number of draws to find a desirable Synthetic Population")
        synPopDrawsEdit = QSpinBox()
        synPopDrawsLabel.setBuddy(synPopDrawsEdit)
        synPopDrawsEdit.setRange(0,  50)
        synPopDrawsEdit.setValue(self.project.parameters.synPopDraws)
        #synPopDrawsEdit.setValue(SYNTHETIC_POP_MAX_DRAWS)

        synPopPValTolLabel = QLabel("Tolerance level of the P-value for the desirable Synthetic Population")
        synPopPValTolEdit = QLineEdit()
        synPopPValTolLabel.setBuddy(synPopPValTolEdit)
        synPopPValTolEdit.setText('%s' %self.project.parameters.synPopPTol)
        #synPopPValTolEdit.setText('%s' %SYNTHETIC_POP_PVALUE_TOLERANCE)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        ipfLabel = QLabel("IPF related parameters:")
        vLayout11 = self.vLayout(ipfTolLabel, ipfMaxIterLabel)
        vLayout12 = self.vLayout(ipfTolEdit, ipfMaxIterEdit)
        
        hLayout1 = self.hLayout(vLayout11, vLayout12)

        ipuLabel = QLabel("IPU related parameters:")
        vLayout21 = self.vLayout(ipuTolLabel, ipuMaxIterLabel)
        vLayout22 = self.vLayout(ipuTolEdit, ipuMaxIterEdit)
        
        hLayout2 = self.hLayout(vLayout21, vLayout22)

        synLabel = QLabel("Synthetic Population draws related parameters:")
        vLayout31 = self.vLayout(synPopDrawsLabel, synPopPValTolLabel)
        vLayout32 = self.vLayout(synPopDrawsEdit, synPopPValTolEdit)
        
        hLayout3 = self.hLayout(vLayout31, vLayout32)

        vLayout = QVBoxLayout()
                          
        vLayout.addWidget(ipfLabel)
        vLayout.addLayout(hLayout1)
        vLayout.addWidget(Separator())
        vLayout.addWidget(ipuLabel)
        vLayout.addLayout(hLayout2)
        vLayout.addWidget(Separator())
        vLayout.addWidget(synLabel)
        vLayout.addLayout(hLayout3)

        vLayout.addWidget(dialogButtonBox)

        self.setLayout(vLayout)
        
        self.connect(dialogButtonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))        


        #Connect the edit events with updating the self.project.parameter variables
        
        #self.connect(

    


    def vLayout(self, widget1, widget2):
        
        layout = QVBoxLayout()
        layout.addWidget(widget1)
        layout.addWidget(widget2)

        return layout

    def hLayout(self, layout1, layout2):
        
        layout = QHBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        
        return layout
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = 1
    form = ParametersDialog(a)
    #form = TabWidget(a)
    form.show()
    print app.exec_()
