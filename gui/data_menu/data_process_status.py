# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from __future__ import with_statement
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pums_data import AutoImportPUMSData, UserImportSampleData
from sf_data import AutoImportSFData, UserImportControlData
from geocorr_data import AutoImportGeocorrData, UserImportGeocorrData
from shape_data import Shapes
from misc.errors import FileError


class DataDialog(QDialog):
    def __init__(self, project, parent = None):
        super(DataDialog, self).__init__(parent)
        self.project = project
        self.setFixedSize(QSize(600, 300))
        self.setWindowTitle("Import")
        self.setWindowIcon(QIcon("./images/fileimport.png"))

        self.move(100,100)

        self.dialogButtonBox = QDialogButtonBox()
        ok = QPushButton("Ok")
        self.dialogButtonBox.addButton(ok, QDialogButtonBox.ActionRole)

        start = QPushButton("Start")
        self.dialogButtonBox.addButton(start, QDialogButtonBox.ActionRole)

        self.dialogButtonBox.addButton(QDialogButtonBox.Cancel)

        ok.setEnabled(False)

        self.GeocorrHousingLayout = CheckLabel("a. Processing geographic correspondence data", "incomplete")
        self.SampleHousingLayout = CheckLabel("b. Processing housing sample data", "incomplete")
        self.SamplePersonLayout = CheckLabel("c. Processing person sample data", "incomplete")
        self.ControlHousingLayout = CheckLabel("d. Processing housing marginals data", "incomplete")
        self.ControlPersonLayout = CheckLabel("e. Processing person marginals data", "incomplete")
        self.RegionShapeLayout = CheckLabel("f. Processing regional shape files", "incomplete")

        importWarning = QLabel("""<font color = blue>Note: Please click on <b>Start</b> to begin importing data."""
                               """</font>""")

        #self.detailsTextEdit = QTextEdit()
        #self.detailsTextEdit.setMinimumHeight(250)

        layout = QVBoxLayout()
        layout.addLayout(self.GeocorrHousingLayout)
        layout.addLayout(self.SampleHousingLayout)
        layout.addLayout(self.SamplePersonLayout)
        layout.addLayout(self.ControlHousingLayout)
        layout.addLayout(self.ControlPersonLayout)
        layout.addLayout(self.RegionShapeLayout)
        layout.addWidget(importWarning)
        #layout.addWidget(self.detailsTextEdit)
        layout.addWidget(self.dialogButtonBox)


        self.setLayout(layout)

        self.connect(self.dialogButtonBox, SIGNAL("clicked(QAbstractButton *)"), self.start)
        self.connect(self.dialogButtonBox, SIGNAL("rejected()"), self, SLOT("reject()"))


    def start(self, button):
        for i in self.dialogButtonBox.buttons():
            if i.text() == "Start" or i.text() == "Cancel":
                i.setVisible(False)
            else:
                i.setEnabled(True)

        if button.text() == 'Start':
            self.geocorr()
            self.sample()
            self.control()
            self.shapes()

        if button.text() == 'Ok':
            self.close()


    def shapes(self):
        shapesDataInstance = Shapes(self.project)
        try:
            shapesDataInstance.downloadShapes()
            self.RegionShapeLayout.changeStatus(True)
        except Exception, e:
            print "Exception: %s" %e
            self.RegionShapeLayout.changeStatus(False)



    def geocorr(self):
        # GEOCORR FILE
        if self.project.geocorrUserProv.userProv:
            # IMPORTING USER PROVIDED FILES
            importGeocorrInstance = UserImportGeocorrData(self.project)
            try:
                importGeocorrInstance.createGeocorrTable()
                self.GeocorrHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.GeocorrHousingLayout.changeStatus(False)

        else:
            # IMPORTING FILES AUTOMATICALLY
            importGeocorrInstance = AutoImportGeocorrData(self.project)
            try:
                importGeocorrInstance.createGeocorrTable()
                self.GeocorrHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.GeocorrHousingLayout.changeStatus(False)
        importGeocorrInstance.projectDBC.dbc.close()

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
                self.importPUMSInstance.checkHousingPUMSTable()
                self.SampleHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.SampleHousingLayout.changeStatus(False)
                # Person PUMS
            try:
                self.importPUMSInstance.checkPersonPUMSTable()
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
                self.importSFInstance.downloadSFData()
                self.importSFInstance.createRawSFTable()
                self.importSFInstance.createMasterSFTable()
                self.importSFInstance.createMasterSubSFTable()
                self.ControlHousingLayout.changeStatus(True)
            except FileError, e:
                print e
                self.ControlHousingLayout.changeStatus(False)

            # Person Controls/Marginals
            try:
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


