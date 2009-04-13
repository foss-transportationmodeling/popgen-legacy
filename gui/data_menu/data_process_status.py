from __future__ import with_statement
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pums_data import AutoImportPUMSData, UserImportSampleData
from sf_data import AutoImportSFData, UserImportControlData
from misc.errors import FileError


class DataDialog(QDialog):
    def __init__(self, project, parent = None):
        super(DataDialog, self).__init__(parent)
        self.project = project
        self.setFixedSize(QSize(600, 200))
        self.setWindowTitle("PopSim: Processing Data")
        self.setWindowIcon(QIcon("./images/popsyn"))

        self.move(100,100)

        self.dialogButtonBox = QDialogButtonBox()
        ok = QPushButton("Ok")
        self.dialogButtonBox.addButton(ok, QDialogButtonBox.ActionRole)

        start = QPushButton("Start")
        self.dialogButtonBox.addButton(start, QDialogButtonBox.ActionRole)

        ok.setEnabled(False)

        self.SampleHousingLayout = CheckLabel("1. Processing Housing PUMS Data", "incomplete")
        self.SamplePersonLayout = CheckLabel("2. Processing Person PUMS Data", "incomplete")
        self.ControlHousingLayout = CheckLabel("3. Processing Housing Summary Data", "incomplete")
        self.ControlPersonLayout = CheckLabel("4. Processing Person Summary Data", "incomplete")

        #self.detailsTextEdit = QTextEdit()
        #self.detailsTextEdit.setMinimumHeight(250)

        layout = QVBoxLayout()
        layout.addLayout(self.SampleHousingLayout)
        layout.addLayout(self.SamplePersonLayout)
        layout.addLayout(self.ControlHousingLayout)
        layout.addLayout(self.ControlPersonLayout)
        #layout.addWidget(self.detailsTextEdit)
        layout.addWidget(self.dialogButtonBox)


        self.setLayout(layout)

        self.connect(self.dialogButtonBox, SIGNAL("clicked(QAbstractButton *)"), self.start)



    def start(self, button):
        for i in self.dialogButtonBox.buttons():
            if i.text() == "Start":
                i.setVisible(False)
            else:
                i.setEnabled(True)

        if button.text() == 'Start':
            #self.geocorr()
            import time
            
            ti = time.time()
            self.sample()
            print 'Time elapsed- %.4f' %(time.time()-ti)            

            ti = time.time()
            self.control()
            print 'Time elapsed- %.4f' %(time.time()-ti)






        if button.text() == 'Ok':
            self.close()

    def geocorr(self):
        # GEOCORR FILE
        if self.project.geocorrUserProv.userProv:
            # IMPORTING USER PROVIDED FILES
            try:
                pass
            except FileError, e:
                pass

        else:
            # IMPORTING FILES AUTOMATICALLY
            try:
                pass
            except FileError, e:
                pass

    def sample(self):
        # SAMPLE FILES
        if self.project.sampleUserProv.userProv:
            # IMPORTING USER PROVIDED FILES
            self.importSampleInstance = UserImportSampleData(self.project)
            # Housing Sample
            try:
                self.importSampleInstance.createHhldTable()
                self.importSampleInstance.createGQTable()
                self.SampleHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.SampleHousingLayout.changeStatus(False)
            # Person Sample
            try:
                self.importSampleInstance.createPersonTable()
                self.SamplePersonLayout.changeStatus(True)
            except FileError, e:
                print e
                self.SamplePersonLayout.changeStatus(False)
            self.importSampleInstance.projectDBC.dbc.close()

        else:
            # IMPORTING FILES AUTOMATICALLY
            self.importPUMSInstance = AutoImportPUMSData(self.project)
            # Housing PUMS
            try:
                self.SampleHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.SampleHousingLayout.changeStatus(False)
                # Person PUMS
            try:
                self.SamplePersonLayout.changeStatus(True)
            except FileError, e:
                print e
                self.SamplePersonLayout.changeStatus(False)
            self.importPUMSInstance.projectDBC.dbc.close()

    def control(self):
        # CONTROL/MARGINAL FILES
        if self.project.controlUserProv.userProv:
            # IMPORTING USER PROVIDED FILES
            self.importControlInstance = UserImportControlData(self.project)
            # Housing Controls
            try:
                
                self.importControlInstance.createHhldTable()
                self.importControlInstance.createGQTable()
                self.ControlHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.ControlHousingLayout.changeStatus(False)
            # Person Controls
            try:
                self.importControlInstance.createPersonTable()
                self.ControlPersonLayout.changeStatus(True)
            except FileError, e:
                print e
                self.ControlPersonLayout.changeStatus(False)
            self.importControlInstance.projectDBC.dbc.close()

        else:
            # IMPORTING FILES AUTOMATICALLY
            self.importSFInstance = AutoImportSFData(self.project)
            # Housing Controls/Marginals
            try:
                #self.importSFInstance.createHousingSFTable()
                self.ControlHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.ControlHousingLayout.changeStatus(False)

            # Person Controls/Marginals
            try:
                #self.importSFInstance.createPersonSFTable()
                self.ControlPersonLayout.changeStatus(True)
            except FileError, e:
                print e
                self.ControlPersonLayout.changeStatus(False)                
            self.importSFInstance.projectDBC.dbc.close()



class CheckLabel(QHBoxLayout):
    def __init__(self, label, checkStatus, parent = None):
        super(CheckLabel, self).__init__(parent)
        label = QLabel("%s" %label)
        label.setMinimumSize(400,30)

        self.labelCheck = QLabel()
        self.addWidget(label)
        self.addWidget(self.labelCheck)
        self.changeStatus(checkStatus)

    def changeStatus(self, checkStatus):
        self.labelCheck.setPixmap(QPixmap("./images/%s" %(checkStatus)))

if __name__ == "__main__":
    pass


