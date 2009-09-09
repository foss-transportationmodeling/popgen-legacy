# PopGen 1.0 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from __future__ import with_statement

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
from misc.errors import FileError

import pickle, os


class OpenProject(QFileDialog):
    def __init__(self, parent=None):
        super(OpenProject, self).__init__(parent)
        self.file = self.getOpenFileName(parent, "Browse to select file", "/home",
                                         "PopGen File (*.pop)")




class SaveFile(QFileDialog):
    def __init__(self, project, fileType, tablename=None, treeParent=None, parent=None):
        super(SaveFile, self).__init__(parent)
        self.project = project
        self.fileType = fileType
        self.tablename = tablename
        self.treeParent = treeParent
        if self.fileType == 'csv':
            self.fileSep = ','
        elif self.fileType == 'dat':
            self.fileSep = '\t'
        self.folder = self.getExistingDirectory(self, QString("Results Location..."),
                                                "%s/%s" %(self.project.location, self.project.filename),
                                                QFileDialog.ShowDirsOnly)

        if not self.folder.isEmpty():
            if not self.tablename:
                self.save()
            else:
                self.saveSelectedTable()

    def saveSummaryStats(self):
        pass


    def save(self):
        scenarioDatabase = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)
        projectDBC = createDBC(self.project.db, scenarioDatabase)
        projectDBC.dbc.open()

        query = QSqlQuery(projectDBC.dbc)

        filename = '%s/housing_synthetic_data.%s' %(self.folder, self.fileType)
        check = self.checkIfFileExists(filename)
        if check == 0:
            os.remove(filename)
        elif check < 2:
            if not query.exec_("""select * from housing_synthetic_data into outfile """
                               """'%s/housing_synthetic_data.%s' fields terminated by '%s'"""
                               %(self.folder, self.fileType, self.fileSep)):
                raise FileError, query.lastError().text()

        filename = '%s/person_synthetic_data.%s' %(self.folder, self.fileType)
        check = self.checkIfFileExists(filename)
        if check == 0:
            os.remove(filename)
        elif check  < 2:
            if not query.exec_("""select * from person_synthetic_data into outfile """
                               """'%s/person_synthetic_data.%s' fields terminated by '%s'"""
                               %(self.folder, self.fileType, self.fileSep)):
                raise FileError, query.lastError().text()



        projectDBC.dbc.close()

    def saveSelectedTable(self):
        if self.treeParent == "Project Tables":
            database = self.project.name
        if self.treeParent == "Scenario Tables":
            database = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)

        projectDBC = createDBC(self.project.db, database)
        projectDBC.dbc.open()

        query = QSqlQuery(projectDBC.dbc)

        filename = '%s/%s.%s' %(self.folder, self.tablename, self.fileType)
        check = self.checkIfFileExists(filename)
        if check == 0:
            os.remove(filename)
        elif check < 2:
            if not query.exec_("""select * from %s into outfile """
                               """'%s' fields terminated by '%s'"""
                               %(self.tablename, filename, self.fileSep)):
                raise FileError, query.lastError().text()


        projectDBC.dbc.close()


    def checkIfFileExists(self, file):
        try:
            fileInfo = os.stat(file)

            reply = QMessageBox.question(None, "Import",
                                         QString("""File %s exists. Would you like to overwrite?""" %(file)),
                                         QMessageBox.Yes| QMessageBox.No)

            if reply == QMessageBox.Yes:
                return 0
            else:
                return 2
        except WindowsError, e:
            #print 'Warning: File - %s not present' %(file)
            return 1




