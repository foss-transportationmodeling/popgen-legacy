from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from database.createDBConnection import createDBC
from misc.widgets import *

import os, shutil


class SummaryPage(QWizardPage):
    def __init__(self, parent=None):
        super(SummaryPage, self).__init__(parent)

        self.projectLocationDummy = False
        self.projectDatabaseDummy = False

        self.setTitle("Step 6: Project Summary")
        vlayoutCol1 = QVBoxLayout()
        vlayoutCol1.addWidget(QLabel("Project name"))
        vlayoutCol1.addWidget(QLabel("Project location"))
        vlayoutCol1.addWidget(QLabel("Project description"))
        vlayoutCol1.addWidget(QLabel("Selected counties"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel("Geographic resolution of population synthesis"))
        vlayoutCol1.addWidget(QLabel("Geographic correspondence data provided by the user"))
        vlayoutCol1.addWidget(QLabel("Location of the geographic correspondence file"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel("Location data provided by the user"))
        vlayoutCol1.addWidget(QLabel("Location of the household sample file"))
        vlayoutCol1.addWidget(QLabel("Location of the group quarter sample file"))
        vlayoutCol1.addWidget(QLabel("Location of the person sample file"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel("Marginals data provided by the user"))
        vlayoutCol1.addWidget(QLabel("Location of the household marginals data file"))
        vlayoutCol1.addWidget(QLabel("Location of the group quarter marginals data file"))
        vlayoutCol1.addWidget(QLabel("Location of the person marginals data file"))


        vlayoutCol2 = QVBoxLayout()

        self.projectNameLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.projectNameLineEdit)

        self.projectLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.projectLocationLineEdit)

        self.projectDescLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.projectDescLineEdit)

        self.projectRegionLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.projectRegionLineEdit)

        vlayoutCol2.addWidget(Separator())

        #self.projectResolutionLineEdit = DisplayLineEdit()
        self.projectResolutionComboBox = ComboBoxFile()
        self.projectResolutionComboBox.setEnabled(False)
        self.projectResolutionComboBox.addItems(['County', 'Census Tract', 'Census Blockgroup'])
        vlayoutCol2.addWidget(self.projectResolutionComboBox)

        self.geocorrUserProvLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.geocorrUserProvLineEdit)

        self.geocorrUserProvLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.geocorrUserProvLocationLineEdit)

        vlayoutCol2.addWidget(Separator())

        self.sampleUserProvLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.sampleUserProvLineEdit)

        self.sampleHHLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.sampleHHLocationLineEdit)

        self.sampleGQLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.sampleGQLocationLineEdit)

        self.samplePersonLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.samplePersonLocationLineEdit)


        vlayoutCol2.addWidget(Separator())

        self.controlUserProvLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.controlUserProvLineEdit)

        self.controlHHLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.controlHHLocationLineEdit)

        self.controlGQLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.controlGQLocationLineEdit)

        self.controlPersonLocationLineEdit = DisplayLineEdit()
        vlayoutCol2.addWidget(self.controlPersonLocationLineEdit)


        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayoutCol1)
        hlayout.addLayout(vlayoutCol2)
        self.setLayout(hlayout)


    def fillPage(self, project):
        self.project = project
        self.projectNameLineEdit.setText(self.project.name)
        self.projectLocationLineEdit.setText(self.project.location)
        self.projectDescLineEdit.setText(self.project.description)
        dummy = ""
        if self.project.region is not None:
            for i in self.project.region.keys():
                dummy = dummy + i + ", "+ self.project.region[i]+ "; "
        self.projectRegionLineEdit.setText("%s"%dummy[:-2])
        #self.projectResolutionLineEdit.setText(self.project.resolution)
        self.projectResolutionComboBox.findAndSet(self.project.resolution)

        geocorrUserProv = self.convertBoolToString(self.project.geocorrUserProv.userProv)
        self.geocorrUserProvLineEdit.setText("%s" %geocorrUserProv)
        self.geocorrUserProvLocationLineEdit.setText(self.project.geocorrUserProv.location)

        sampleUserProv = self.convertBoolToString(self.project.sampleUserProv.userProv)
        self.sampleUserProvLineEdit.setText("%s" %sampleUserProv)
        self.sampleHHLocationLineEdit.setText(self.project.sampleUserProv.hhLocation)
        self.sampleGQLocationLineEdit.setText(self.project.sampleUserProv.gqLocation)
        self.samplePersonLocationLineEdit.setText(self.project.sampleUserProv.personLocation)

        controlUserProv = self.convertBoolToString(self.project.controlUserProv.userProv)
        self.controlUserProvLineEdit.setText("%s" %controlUserProv)
        self.controlHHLocationLineEdit.setText(self.project.controlUserProv.hhLocation)
        self.controlGQLocationLineEdit.setText(self.project.controlUserProv.gqLocation)
        self.controlPersonLocationLineEdit.setText(self.project.controlUserProv.personLocation)


    def convertBoolToString(self, value):
        if value:
            text = 'Yes'
        else:
            text = 'No, default data will be used'
        return text
    

    def enableEditableWidgets(self):
        self.projectDescLineEdit.setEnabled(True)
        self.projectResolutionComboBox.setEnabled(True)
        #self.geocorrUserProvLineEdit.setEnabled(True)
        #self.geocorrUserProvLocationLineEdit.setEnabled(True)
        #self.sampleUserProvLineEdit.setEnabled(True)
        #self.sampleHHLocationLineEdit.setEnabled(True)
        #self.sampleGQLocationLineEdit.setEnabled(True)
        #self.samplePersonLocationLineEdit.setEnabled(True)
        #self.controlUserProvLineEdit.setEnabled(True)
        #self.controlHHLocationLineEdit.setEnabled(True)
        #self.controlGQLocationLineEdit.setEnabled(True)
        #self.controlPersonLocationLineEdit.setEnabled(True)
        pass


    def updateProject(self):
        self.project.description = self.projectDescLineEdit.text()
        resolutionText = self.projectResolutionComboBox.currentText()
        if resolutionText == "Census Tract":
            resolution = 'Tract'
        elif resolutionText == "Census Blockgroup":
            resolution = 'Blockgroup'
        elif resolutionText == 'Traffic Analysis Zone (TAZ)':
            resolution = 'TAZ'
        else:
            resolution = 'County'

        self.project.resolution = resolution


    def isComplete(self):
        if self.projectLocationDummy and self.projectDatabaseDummy:
            return True
        else:
            return False

    def checkFileLocation(self, filePath):
        try:
            open(filePath, 'r')
        except IOError, e:
            raise IOError, e

    def checkProjectLocation(self, projectLocation, projectName):
        try:
            os.makedirs("%s/%s/results" %(projectLocation, projectName))
            self.projectLocationDummy = True
        except WindowsError, e:
            reply = QMessageBox.question(None, "Project Setup Wizard",
                                         QString("""%s. \n\nDo you wish"""
                                                 """ to keep the previous data?"""
                                                 """\n    If Yes then re-scpecify the project location. """
                                                 """\n    If you wish to delete the previous data select No."""%e),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "Project Setup Wizard",
                                               QString("""Are you sure you want to continue?"""),
                                               QMessageBox.Yes|QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    shutil.rmtree("%s/%s" %(projectLocation, projectName))
                    os.makedirs("%s/%s/results" %(projectLocation, projectName))
                    self.projectLocationDummy = True
                else:
                    self.projectLocationDummy = False
            else:
                self.projectLocationDummy = False
        self.emit(SIGNAL("completeChanged()"))

    def checkProjectDatabase(self, db, projectName):
        projectDBC = createDBC(db)
        projectDBC.dbc.open()

        query = QSqlQuery(projectDBC.dbc)
        if not query.exec_("""Create Database %s""" %(projectName)):
            reply = QMessageBox.question(None, "Project Setup Wizard",
                                         QString("""%s. \n\n"""
                                                 """Do you wish to keep the old MySQL database?"""
                                                 """\n    If Yes then re-specify the project name."""
                                                 """\n    If you wish to delete select No."""%query.lastError().text()),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "Project Setup Wizard",
                                               QString("""Are you sure you want to continue?"""),
                                               QMessageBox.Yes|QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    if not query.exec_("""Drop Database %s""" %(projectName)):
                        print "FileError: %s" %(query.lastError().text())
                        projectDBC.dbc.close()
                        self.projectDatabaseDummy = False
                    if not query.exec_("""Create Database %s""" %(projectName)):
                        print "FileError: %s" %(query.lastError().text())
                        projectDBC.dbc.close()
                        self.projectDatabaseDummy = False
                    projectDBC.dbc.close()
                    self.projectDatabaseDummy = True
                else:
                    projectDBC.dbc.close()
                    self.projectDatabaseDummy = False
            else:
                projectDBC.dbc.close()
                self.projectDatabaseDummy =  False
        else:
            projectDBC.dbc.close()
            self.projectDatabaseDummy = True


        self.emit(SIGNAL("completeChanged()"))

