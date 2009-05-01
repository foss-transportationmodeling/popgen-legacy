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

        self.setTitle("Step 6: Summary")
        vlayoutCol1 = QVBoxLayout()
        vlayoutCol1.addWidget(QLabel("Project Name:"))
        vlayoutCol1.addWidget(QLabel("Project Location:"))
        vlayoutCol1.addWidget(QLabel("Project Description"))
        vlayoutCol1.addWidget(QLabel("Selected Counties:"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel("Resolution of population Synthesis:"))
        vlayoutCol1.addWidget(QLabel("Geographic correspondence data provided by the user:"))
        vlayoutCol1.addWidget(QLabel("Location of the geographic correspondence file:"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel(" data provided by the user:"))
        vlayoutCol1.addWidget(QLabel("Location of the household sample file:"))
        vlayoutCol1.addWidget(QLabel("Location of the group quarter sample file:"))
        vlayoutCol1.addWidget(QLabel("Location of the person sample file:"))
        vlayoutCol1.addWidget(Separator())
        vlayoutCol1.addWidget(QLabel("Control data provided by the user:"))
        vlayoutCol1.addWidget(QLabel("Location of the household control data file:"))
        vlayoutCol1.addWidget(QLabel("Location of the group quarter control data file:"))
        vlayoutCol1.addWidget(QLabel("Location of the person control data file:"))


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
        self.projectResolutionComboBox.addItems(['County', 'Tract', 'Blockgroup'])
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

        self.geocorrUserProvLineEdit.setText("%s" %self.project.geocorrUserProv.userProv)
        self.geocorrUserProvLocationLineEdit.setText(self.project.geocorrUserProv.location)
        self.sampleUserProvLineEdit.setText("%s" %self.project.sampleUserProv.userProv)
        self.sampleHHLocationLineEdit.setText(self.project.sampleUserProv.hhLocation)
        self.sampleGQLocationLineEdit.setText(self.project.sampleUserProv.gqLocation)
        self.samplePersonLocationLineEdit.setText(self.project.sampleUserProv.personLocation)
        self.controlUserProvLineEdit.setText("%s" %self.project.controlUserProv.userProv)
        self.controlHHLocationLineEdit.setText(self.project.controlUserProv.hhLocation)
        self.controlGQLocationLineEdit.setText(self.project.controlUserProv.gqLocation)
        self.controlPersonLocationLineEdit.setText(self.project.controlUserProv.personLocation)


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
        self.project.resolution = self.projectResolutionComboBox.currentText()


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
            reply = QMessageBox.question(None, "PopSim: New Project Wizard",
                                         QString("""Database Error: %s. \n\nDo you wish"""
                                                 """ to keep the previous data?"""
                                                 """\n    If Yes then rescpecify project location. """
                                                 """\n    If you wish to delete the previous data press No."""%e),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "PopSim: New Project Wizard",
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
            reply = QMessageBox.question(None, "PopSim: Processing Data",
                                         QString("""QueryError: %s. \n\n"""
                                                 """Do you wish to keep the old MySQL database?"""
                                                 """\n    If Yes then respecify the project name."""
                                                 """\n    If you wish to delete press No."""%query.lastError().text()),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "PopSim: Processing Data",
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
