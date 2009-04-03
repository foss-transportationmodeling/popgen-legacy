from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import shutil, urllib, os

from database.createDBConnection import createDBC
from summary_page import SummaryPage
from data_menu.data_process_status import DataDialog



class QTreeWidgetCMenu(QTreeWidget):
    def __init__(self, project=None, parent = None):
        self.parent = parent
        super(QTreeWidgetCMenu, self).__init__(parent)
        self.project = project

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        importDataAction = menu.addAction("&Import Data")
        editProjectAction = menu.addAction("Edit Project")
        self.connect(importDataAction, SIGNAL("triggered()"), self.importData)
        self.connect(editProjectAction, SIGNAL("triggered()"), self.editProject)
        if self.item.parent() is None:
            menu.exec_(event.globalPos())

    def click(self, item, column):
        self.item = item
        

    def editProject(self):
        #print 'editing project'
        editWidget = QWizard()
        editWidget.setWizardStyle(QWizard.ClassicStyle)
        editWidget.setOption(QWizard.NoBackButtonOnStartPage)
        self.page = SummaryPage()
        self.page.projectLocationDummy = True
        self.page.projectDatabaseDummy = True
        self.page.fillPage(self.project)
        self.page.enableEditableWidgets()
        editWidget.addPage(self.page)


        if editWidget.exec_():
            self.page.updateProject()
            self.project = self.page.project
            self.project.save()
            self.populate()

    def importData(self):
        #QMessageBox.information(None, "Check", "Import Data", QMessageBox.Ok)
        dataprocesscheck = DataDialog(self.project)
        dataprocesscheck.exec_()



    def populate(self):
        self.setEnabled(True)
        self.clear()
        
        projectAncestor = QTreeWidgetItem(self, [QString("Project: " + self.project.name)])
        informationParent = QTreeWidgetItem(projectAncestor, [QString("Information")])
        
        dummy = ""
        if self.project.region is not None:
            for i in self.project.region.keys():
                dummy = dummy + i + ", "+ self.project.region[i]+ "; "

        informationItems = {"Location":self.project.location, 
                            "Description":self.project.description,
                            "Region":dummy,
                            "Resolution":self.project.resolution}
        for i,j in informationItems.items():
            child = QTreeWidgetItem(informationParent, [i, QString(j)])
        
        geocorrParent = QTreeWidgetItem(projectAncestor, [QString("Geographic Correspondence")])
        geocorrItems = {"User Provided":self.project.geocorrUserProv.userProv, 
                        "Location":self.project.geocorrUserProv.location}
        
        for i,j in geocorrItems.items():
            child = QTreeWidgetItem(geocorrParent, [i, QString("%s"%j)])

        sampleParent = QTreeWidgetItem(projectAncestor, [QString("Sample")])
        sampleItems = {"User Provided":self.project.sampleUserProv.userProv,
                       "Household Data Location": self.project.sampleUserProv.hhLocation,
                       "GQ Data Location": self.project.sampleUserProv.gqLocation,
                       "Person Data Location": self.project.sampleUserProv.personLocation}

        for i,j in sampleItems.items():
            child = QTreeWidgetItem(sampleParent, [i, QString("%s"%j)])

        controlParent = QTreeWidgetItem(projectAncestor, [QString("Control")])
        controlItems = {"User Provided":self.project.controlUserProv.userProv,
                       "Household Data Location": self.project.controlUserProv.hhLocation,
                       "GQ Data Location": self.project.controlUserProv.gqLocation,
                       "Person Data Location": self.project.controlUserProv.personLocation}

        for i,j in controlItems.items():
            child = QTreeWidgetItem(controlParent, [i, QString("%s"%j)])

        dbParent = QTreeWidgetItem(projectAncestor, [QString("Database")])
        dbItems = {"Hostname":self.project.db.hostname,
                   "Username":self.project.db.username,
                   "Password":self.project.db.password}

        for i,j in dbItems.items():
            child = QTreeWidgetItem(dbParent, [QString(i), QString(j)])

        tableParent = QTreeWidgetItem(projectAncestor, [QString("Data Tables")])
        
            

        self.expandItem(projectAncestor)
        self.expandItem(informationParent)
        self.expandItem(geocorrParent)
        self.expandItem(sampleParent)
        self.expandItem(controlParent)
        self.expandItem(dbParent)

