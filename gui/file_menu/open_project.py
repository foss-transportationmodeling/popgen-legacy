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
from misc.widgets import VariableSelectionDialog

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
        if check < 2:
            hhldVariables = self.getVariables('hhld_sample', query)
            hhldSelVariables = self.getSelectedVariables(hhldVariables, self.project.hhldVars, 
                                                         "Select Household Variables to Add to Synthetic Data")
            hhldvarstr = ""
            for  i in hhldSelVariables:
                hhldvarstr = hhldvarstr + '%s,' %i
            
            if not query.exec_("""drop table temphou1"""):
                print "FileError:%s" %query.lastError().text()
            if not query.exec_("""create table temphou1 select housing_synthetic_data.*, %s from housing_synthetic_data"""
                               """ left join hhld_sample using (serialno)""" %(hhldvarstr[:-1])):
                raise FileError, query.lastError().text()
            if not query.exec_("""alter table temphou1 add index(serialno)"""):
                raise FileError, query.lastError().text()



            gqVariables = self.getVariables('gq_sample', query)
            gqSelVariables = self.getSelectedVariables(gqVariables, self.project.gqVars, 
                                                         "Select Groupquarter Variables to Add to Synthetic Data")
            gqvarstr = ""
            for  i in gqSelVariables:
                gqvarstr = gqvarstr + '%s,' %i
            
            if not query.exec_("""drop table temphou2"""):
                print "FileError:%s" %query.lastError().text()
            if not query.exec_("""create table temphou2 select temphou1.*, %s from temphou1"""
                               """ left join gq_sample using (serialno)""" %(gqvarstr[:-1])):
                raise FileError, query.lastError().text()

            if not query.exec_("""select * from temphou2 into outfile """
                               """'%s/housing_synthetic_data.%s' fields terminated by '%s'"""
                               %(self.folder, self.fileType, self.fileSep)):
                raise FileError, query.lastError().text()

            if not query.exec_("""drop table temphou1"""):
                print "FileError:%s" %query.lastError().text()
            if not query.exec_("""drop table temphou2"""):
                print "FileError:%s" %query.lastError().text()

        filename = '%s/person_synthetic_data.%s' %(self.folder, self.fileType)
        check = self.checkIfFileExists(filename)
        if check == 0:
            os.remove(filename)
        if check  < 2:
            personVariables = self.getVariables('person_sample', query)
            personSelVariables = self.getSelectedVariables(personVariables, self.project.personVars, 
                                                           "Select Person Variables to Add to Synthetic Data")

            personvarstr = ""
            for  i in personSelVariables:
                personvarstr = personvarstr + '%s,' %i
            
            if not query.exec_("""drop table tempperson"""):
                print "FileError:%s" %query.lastError().text()
            if not query.exec_("""create table tempperson select person_synthetic_data.*, %s from person_synthetic_data"""
                               """ left join person_sample using (serialno)""" %(personvarstr[:-1])):
                raise FileError, query.lastError().text()

            if not query.exec_("""select * from tempperson into outfile """
                               """'%s/person_synthetic_data.%s' fields terminated by '%s'"""
                               %(self.folder, self.fileType, self.fileSep)):
                raise FileError, query.lastError().text()
            if not query.exec_("""drop table tempperson"""):
                print "FileError:%s" %query.lastError().text()

        projectDBC.dbc.close()


    def getVariables(self, tablename, query):
        if not query.exec_("""desc %s""" %(tablename)):
            raise FileError, query.lastError().text()
        
        varDict = {}
        while query.next():
            varname = query.value(0).toString()
            varDict['%s' %varname] = ""
            
        return varDict
        
    
    def getSelectedVariables(self, varDict, defaultVariables, title, icon=None, warning=None):
        selDia = VariableSelectionDialog(varDict, defaultVariables, title, icon, warning)

        selVariables = []
        if selDia.exec_():
            selVarCount = selDia.selectedVariableListWidget.count()
            if selVarCount > 0:
                for i in range(selVarCount):
                    selVariables.append(selDia.selectedVariableListWidget.item(i).text())
            return selVariables
            




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




