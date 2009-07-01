import urllib
import os
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
from misc.errors import FileError
from misc.utils import UnzipFile
from import_data import ImportUserProvData, FileProperties

from global_vars import *


class UserImportControlData():
    def __init__(self, project):
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.query = QSqlQuery(self.projectDBC.dbc)


    def createHhldTable(self):
        check = self.checkIfTableExists('hhld_marginals')

        if check:
            hhldTableQuery = self.mysqlQueries('hhld_marginals', self.project.controlUserProv.hhLocation)

            if not self.query.exec_(hhldTableQuery.query1):
                raise FileError, self.query.lastError().text()

            if not self.query.exec_(hhldTableQuery.query2):
                raise FileError, self.query.lastError().text()

    def createGQTable(self):
        check = self.checkIfTableExists('gq_marginals')

        if check:
            gqLocLen = len(self.project.controlUserProv.gqLocation)
        
            if gqLocLen > 1:
                gqTableQuery = self.mysqlQueries('gq_marginals', self.project.controlUserProv.gqLocation)

                if not self.query.exec_(gqTableQuery.query1):
                    raise FileError, self.query.lastError().text()
            
                if not self.query.exec_(gqTableQuery.query2):
                    raise FileError, self.query.lastError().text()

    def createPersonTable(self):
        check = self.checkIfTableExists('person_marginals')

        if check:
            personTableQuery = self.mysqlQueries('person_marginals', self.project.controlUserProv.personLocation)

            if not self.query.exec_(personTableQuery.query1):
                raise FileError, self.query.lastError().text()

            if not self.query.exec_(personTableQuery.query2):
                raise FileError, self.query.lastError().text()


    def mysqlQueries(self, name, filePath):
        # Generate the mysql queries to import the tables
        fileProp = FileProperties(filePath)
        fileQuery = ImportUserProvData(name, 
                                       filePath, 
                                       fileProp.varNames,
                                       fileProp.varTypes,
                                       fileProp.varNamesDummy, 
                                       fileProp.varTypesDummy)
        return fileQuery

    def checkIfTableExists(self, tablename):
        # 0 - some other error, 1 - overwrite error (table deleted)
        if not self.query.exec_("""create table %s (dummy text)""" %tablename):
            if self.query.lastError().number() == 1050:
                reply = QMessageBox.question(None, "Import",
                                             QString("""A table with name %s already exists. Would you like to overwrite?""" %tablename),
                                             QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not self.query.exec_("""drop table %s""" %tablename):
                        raise FileError, self.query.lastError().text()
                    return 1
                else:
                    return 0
            else:
                raise FileError, self.query.lastError().text()
        else:
            if not self.query.exec_("""drop table %s""" %tablename):
                raise FileError, self.query.lastError().text()
            return 1

class AutoImportSFData():
    def __init__(self, project):
        self.project = project
        self.state = self.project.state
        self.stateAbb = self.project.stateAbb
        self.stateCode = self.project.stateCode

        self.loc = DATA_DOWNLOAD_LOCATION + os.path.sep + self.state + os.path.sep + 'SF'
        self.loc = os.path.realpath(self.loc)
        
        self.countiesSelected = self.project.region.keys()

        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.query = QSqlQuery(self.projectDBC.dbc)

        self.rawSF = RAW_SUMMARY_FILES
        
        self.rawSFNamesNoExt = RAW_SUMMARY_FILES_NOEXT

        #self.downloadSFData()
        #self.createRawSFTable()
        #self.createMasterSFTable()
        #self.createMasterSubSFTable()

    def downloadSFData(self):
        try:
            os.makedirs(self.loc)
            self.retrieveAndStoreSF(self.state)
        except WindowsError, e:
            reply = QMessageBox.question(None, "Import",
                                         QString("""Cannot download data when the data already exists.\n\n"""
                                                 """Would you like to keep the existing files?"""
                                                 """\nHit No if you would like to download the files again."""),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "Import",
                                               QString("""Would you like to continue?"""),
                                               QMessageBox.Yes|QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    self.retrieveAndStoreSF(self.state)
        self.extractSF(self.state)


    def retrieveAndStoreSF(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')
        for i in self.rawSF:
            sf_loc = self.loc + os.path.sep + '%s%s' %(self.stateAbb[state], i)
            urllib.urlretrieve("""http://www2.census.gov/census_2000/"""
                               """datasets/Summary_File_3/%s/%s%s""" %(web_state, self.stateAbb[state], i),
                               sf_loc)

    def extractSF(self, state):
        for i in self.rawSF:
            file = UnzipFile(self.loc, "%s%s" %(self.stateAbb[state],i))
            file.unzip()

    def checkIfTableExists(self, tablename):
        # 0 - some other error, 1 - overwrite error (table deleted)
        if not self.query.exec_("""create table %s (dummy text)""" %tablename):
            if self.query.lastError().number() == 1050:
                reply = QMessageBox.question(None, "Import",
                                             QString("""A table with name %s already exists. Would you like to overwrite?""" %tablename),
                                             QMessageBox.Yes| QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not self.query.exec_("""drop table %s""" %tablename):
                        raise FileError, self.query.lastError().text()
                    return 1
                else:
                    return 0
            else:
                raise FileError, self.query.lastError().text()
        else:
            if not self.query.exec_("""drop table %s""" %tablename):
                raise FileError, self.query.lastError().text()
            return 1


    def createRawSFTable(self):
        # Create raw SF tables which can then be used to create the required summary file tables for use
        # population synthesis

        # First create the state geo table


        if self.checkIfTableExists('sf3filestablescorr'):
            sf3FilesTablesCorrTable = ImportUserProvData("sf3filestablescorr",
                                                         "./data/sf3filestablescorr.csv",
                                                         [], [], True, True)
            if not self.query.exec_(sf3FilesTablesCorrTable.query1):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_(sf3FilesTablesCorrTable.query2):
                raise FileError, self.query.lastError().text()

        tablename = '%sgeo' %(self.stateAbb[self.state])

        if self.checkIfTableExists(tablename):
            if not self.query.exec_("""create table %s (raw text, sumlev float, sfgeoid float, """
                                    """state float, county float, tract  float, bg float, logrecno float)""" 
                                    %tablename):
                raise FileError, self.query.lastError().text()

            geo_loc = os.path.join(self.loc, '%s.uf3'%tablename)
            geo_loc = geo_loc.replace("\\", "/")


            if not self.query.exec_("""load data local infile '%s'"""
                                    """ into table %sgeo (raw)""" %(geo_loc, self.stateAbb[self.state])):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set sumlev = mid(raw, 9, 3)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set sfgeoid = mid(raw, 19, 7)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set state = mid(raw, 30, 2)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set county = mid(raw, 32, 3)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set tract = mid(raw, 56, 6)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set bg = mid(raw, 62, 1)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""update %sgeo set logrecno = mid(raw, 19, 7)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""alter table %sgeo modify logrecno int""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""alter table %sgeo add primary key (logrecno)""" %self.stateAbb[self.state]):
                raise FileError, self.query.lastError().text()

        # Load the other necessary tables
        
        for j in self.rawSFNamesNoExt[1:]:
            variables, variabletypes = self.variableNames(j)
            filename = "%s%s" %(self.stateAbb[self.state], j)
            sf_loc = os.path.join(self.loc, '%s.uf3' %(filename))
            sffile = ImportUserProvData(filename,
                                        sf_loc,
                                        variables, variabletypes, False, False)
            if self.checkIfTableExists(filename):

                if not self.query.exec_(sffile.query1):
                    raise FileError, self.query.lastError().text()
                if not self.query.exec_(sffile.query2):
                    raise FileError, self.query.lastError().text()
                if not self.query.exec_("alter table %s add primary key (logrecno)" %filename):
                    raise FileError, self.query.lastError().text()



    def variableNames(self, filenumber = None, tablenumber = None):
        import copy
        variables = copy.deepcopy(RAW_SUMMARY_FILES_COMMON_VARS)
        variabletypes = copy.deepcopy(RAW_SUMMARY_FILES_COMMON_VARS_TYPE)

        filenumber = str(filenumber).rjust(5, '0')

        if tablenumber is None and filenumber is not None:
            if not self.query.exec_("""select tablenumber, numcat from sf3filestablescorr"""
                                    """ where filenumber = %s order by tablenumber""" %filenumber):
                raise FileError, self.query.lastError().text()
        if tablenumber is not None:
            if not self.query.exec_("""select tablenumber, numcat from sf3filestablescorr"""
                                    """ where tablenumber = %s""" %tablenumber):
                raise FIleError, self.query.lastError().text()
        if filenumber is None and tablenumber is None:
            raise FileError, "Insufficient parameters supplied"


        while self.query.next():
            tablenumber = str(self.query.value(0).toInt()[0]).rjust(3, '0')
            numcat = self.query.value(1).toInt()[0]
            for i in range(numcat):
                colname = 'P'+ tablenumber + str(i+1).rjust(3, '0')
                variables.append(colname)
                variabletypes.append('bigint')
                #print colname

        return variables, variabletypes


    def createMasterSFTable(self):
        import copy
        var1 = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)
        var1string = self.createVariableString(var1)

        var1.remove('logrecno')
        var1.append('temp1.logrecno')
        
        if self.checkIfTableExists('mastersftable'):
            self.checkIfTableExists('temp1')
            self.checkIfTableExists('temp2')
            if not self.query.exec_("""create table temp1 select %s from %sgeo""" 
                                    %(var1string, self.stateAbb[self.state])):
                raise FileError, self.query.lastError().text()

            for j in self.rawSFNamesNoExt[1:]:
                var2, var2types = self.variableNames('%s' %j)
                var1 = var1 + var2[5:]
                var1string = self.createVariableString(var1)
                
                tablename = '%s%s' %(self.stateAbb[self.state], j)
                
                if not self.query.exec_("""create table temp2 select %s from temp1, %s"""
                                        """ where temp1.logrecno = %s.logrecno""" %(var1string, tablename, tablename)):
                    raise FileError, self.query.lastError().text()
                if not self.query.exec_("""drop table temp1"""):
                    raise FileError, self.query.lastError().text()
                if not self.query.exec_("""alter table temp2 rename to temp1"""):
                    raise FileError, self.query.lastError().text()
            
            if not self.query.exec_("""alter table temp1 rename to mastersftable"""):
                raise FileError, self.query.lastError().text()


    def createMasterSubSFTable(self):
        #Based on the resolution import a summary file table for only that resolution

        

        if self.checkIfTableExists('mastersftable%s' %self.project.resolution):
            print self.project.resolution
            if self.project.resolution == 'Blockgroup':
                sumlev = 150
            if self.project.resolution == 'Tract':
                sumlev = 140
            if self.project.resolution == 'County':
                sumlev = 510
            if not self.query.exec_("""create table mastersftable%s """
                                    """select * from mastersftable where sumlev = %s """ 
                                    %(self.project.resolution, sumlev)):
                raise FileError, self.query.lastError().text()

        


    def createVariableString(self, variableList):
        variableString = ""
        for i in variableList:
            variableString = variableString + i + ", "
        return variableString[:-2]


    def createHousingSFTable(self):

        HousingTables = HOUSING_SUMMARY_TABLES

        import copy
        var = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)

        for i in HousingTables:
            var1, var1types = self.variableNames(tablenumber = i)
            var = var + var1[5:]

        varstring = self.createVariableString(var)

        if not self.query.exec_("""create table housing_marginals_%s select %s from mastersftable_%s"""
                                %(self.stateAbb[self.state], varstring, self.stateAbb[self.state])):
                                        
            raise FileError, self.query.lastError().text()

    def createPersonSFTable(self):
        PersonTables = PERSON_SUMMARY_TABLES
        
        import copy
        var = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)

        for i in PersonTables:
            var1, var1types = self.variableNames(tablenumber = i)
            var = var + var1[5:]

        varstring = self.createVariableString(var)

        if not self.query.exec_("""create table person_marginals_%s select %s from mastersftable_%s"""
                                %(self.stateAbb[self.state], varstring, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()
