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
            hhldVariablesDict, hhldVariables = self.getVariables('hhld_sample', query)
            hhldVariablesDict = self.deleteDictEntries(hhldVariablesDict)
            hhldSelVariables = self.getSelectedVariables(hhldVariablesDict, self.project.hhldVars, 
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


            if self.project.gqVars:
                gqVariablesDict, gqVariables = self.getVariables('gq_sample', query)
                gqVariablesDict = self.deleteDictEntries(gqVariablesDict)
                gqSelVariables = self.getSelectedVariables(gqVariablesDict, self.project.gqVars, 
                                                         "Select Groupquarter Variables to Add to Synthetic Data")
                gqvarstr = ""
                for  i in gqSelVariables:
                    gqvarstr = gqvarstr + '%s,' %i
            
                if not query.exec_("""drop table temphou2"""):
                    print "FileError:%s" %query.lastError().text()
                if not query.exec_("""create table temphou2 select temphou1.*, %s from temphou1"""
                                   """ left join gq_sample using (serialno)""" %(gqvarstr[:-1])):
                    raise FileError, query.lastError().text()
            else:
                if not query.exec_("""alter table temphou1 rename to temphou2"""):
                    raise FileError, query.lastError().text()                

            if self.project.sampleUserProv.defSource == "ACS 2005-2007":
                print 'ACS HOUSING DATA MODIFYING THE SERIALNOS'
                if not query.exec_("""drop table temphou3"""):
                    print "FileError:%s" %query.lastError().text()
                if not query.exec_("""alter table temphou2 drop column serialno"""):
                    raise FileError, query.lastError().text()
                if not query.exec_("""alter table temphou2 add index(hhid)"""):
                    raise FileError, query.lastError().text()
                if not query.exec_("""alter table serialcorr add index(hhid)"""):
                    raise FileError, query.lastError().text()
                if not query.exec_("""create table temphou3 select temphou2.*, serialno from temphou2"""
                                   """ left join serialcorr using (hhid)"""):
                    raise FileError, query.lastError().text()

                if not query.exec_("""select * from temphou3 into outfile """
                                   """'%s/housing_synthetic_data.%s' fields terminated by '%s'"""
                                   %(self.folder, self.fileType, self.fileSep)):
                    raise FileError, query.lastError().text()

                housingSynTableVarDict, housingSynTableVars = self.getVariables('temphou3', query)

                if not query.exec_("""drop table temphou3"""):
                    print "FileError:%s" %query.lastError().text()

            else:
                if not query.exec_("""select * from temphou2 into outfile """
                                   """'%s/housing_synthetic_data.%s' fields terminated by '%s'"""
                                   %(self.folder, self.fileType, self.fileSep)):
                    raise FileError, query.lastError().text()

                housingSynTableVarDict, housingSynTableVars = self.getVariables('temphou2', query)
            
            self.storeMetaData(housingSynTableVars, self.folder, 'housing_synthetic_data')
            
            if not query.exec_("""drop table temphou1"""):
                print "FileError:%s" %query.lastError().text()

            if not self.project.gqVars:
                if not query.exec_("""drop table temphou2"""):
                    print "FileError:%s" %query.lastError().text()


        filename = '%s/person_synthetic_data.%s' %(self.folder, self.fileType)
        check = self.checkIfFileExists(filename)
        if check == 0:
            os.remove(filename)
        if check  < 2:
            personVariablesDict, personVariables = self.getVariables('person_sample', query)
            personVariablesDict = self.deleteDictEntries(personVariablesDict)
            personSelVariables = self.getSelectedVariables(personVariablesDict, self.project.personVars, 
                                                           "Select Person Variables to Add to Synthetic Data")

            personvarstr = ""
            for  i in personSelVariables:
                personvarstr = personvarstr + '%s,' %i
            
            if not query.exec_("""drop table tempperson"""):
                print "FileError:%s" %query.lastError().text()
            if not query.exec_("""create table tempperson select person_synthetic_data.*, %s from person_synthetic_data"""
                               """ left join person_sample using (serialno)""" %(personvarstr[:-1])):
                raise FileError, query.lastError().text()

            if self.project.sampleUserProv.defSource == "ACS 2005-2007":
                print 'ACS PERSON DATA MODIFYING THE SERIALNOS'
                if not query.exec_("""drop table tempperson1"""):
                    print "FileError:%s" %query.lastError().text()
                if not query.exec_("""alter table tempperson drop column serialno"""):
                    raise FileError, query.lastError().text()
                if not query.exec_("""alter table tempperson add index(hhid)"""):
                    raise FileError, query.lastError().text()
                if not query.exec_("""create table tempperson1 select tempperson.*, serialno from tempperson"""
                                   """ left join serialcorr using (hhid)"""):
                    raise FileError, query.lastError().text()

                if not query.exec_("""select * from tempperson1 into outfile """
                                   """'%s/person_synthetic_data.%s' fields terminated by '%s'"""
                                   %(self.folder, self.fileType, self.fileSep)):
                    raise FileError, query.lastError().text()

                personSynTableVarDict, personSynTableVars = self.getVariables('tempperson1', query)


                #if not query.exec_("""drop table tempperson1"""):
                #    print "FileError:%s" %query.lastError().text()
            else:
                if not query.exec_("""select * from tempperson into outfile """
                                   """'%s/person_synthetic_data.%s' fields terminated by '%s'"""
                                   %(self.folder, self.fileType, self.fileSep)):
                    raise FileError, query.lastError().text()


                personSynTableVarDict, personSynTableVars = self.getVariables('tempperson', query)
            
            self.storeMetaData(personSynTableVars, self.folder, 'person_synthetic_data')

            #if not query.exec_("""drop table tempperson"""):
            #    print "FileError:%s" %query.lastError().text()


        projectDBC.dbc.close()

    def deleteDictEntries(self, dict):
        print dict
        vars = ['state', 'pumano', 'hhid', 'serialno', 'pnum', 'hhlduniqueid', 'gquniqueid', 'personuniqueid']
        for i in vars:
            try:
                dict.pop(i)
            except:
                pass
        print dict
        return dict


    def storeMetaData(self, varNames, location, tablename):
        f = open('%s/%s_meta.txt' %(location, tablename), 'w')
        col = 1
        for i in varNames:
            f.write('column %s -  %s\n' %(col, i))
            col = col + 1
        f.close()


    def getVariables(self, tablename, query):
        if not query.exec_("""desc %s""" %(tablename)):
            raise FileError, query.lastError().text()
        
        varDict = {}
        varNameList = []
        while query.next():
            varname = query.value(0).toString()
            varDict['%s' %varname] = ""
            varNameList.append(varname)
            
        return varDict, varNameList
        
    
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

        if check < 2:
            if not query.exec_("""select * from %s into outfile """
                               """'%s' fields terminated by '%s'"""
                               %(self.tablename, filename, self.fileSep)):
                raise FileError, query.lastError().text()

        tableVarDict, tableVars = self.getVariables(self.tablename, query)
        self.storeMetaData(tableVars, self.folder, self.tablename)

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




