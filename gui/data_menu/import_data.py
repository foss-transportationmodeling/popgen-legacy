from __future__ import with_statement

import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui.misc.errors import FileError




class FileProperties():
    def __init__(self, filePath):
        with open(filePath, 'r') as f:        
            self.varNames = []
            self.varTypes = []
            
            firstline = f.readline()
            secondline = f.readline()

            if self.checkVarTypes(firstline):
                self.varTypesDummy = True
                self.varTypes = re.split("[,|\t]", firstline[:-1])
                self.varNamesDummy = False
            else:
                self.varTypesDummy = False
                if self.checkVarNames(firstline):
                    self.varNamesDummy = True
                    self.varNames = re.split("[,|\t]", firstline[:-1])
                else:
                    self.varNamesDummy = False
                if self.checkVarTypes(secondline):
                    self.varTypesDummy = True
                    self.varTypes = re.split("[,|\t]", secondline[:-1])
                else:
                    self.varTypesDummy = False

            if self.varNamesDummy and self.varTypesDummy:
                if len(self.varNames) <> len(self.varTypes):
                    raise FileError, "Mismatch in the number of Variable Names and Variable Types"
                

    def checkVarTypes(self, line):
        validVariableTypes = ['tinyint', 'smallint', 'mediumint', 'int','bigint',
                              'float', 'double',
                              'decimal',
                              'bit',
                              'char', 'varchar', 'text', 'binary', 'varbinary', 'blob', 'enum', 'set']
        line = re.split("[,|\t]", line[:-1])
        for i in line:
            try:
                validVariableTypes.index(i.lower())
            except:
                #raise FileError, "Enter a valid variable type definition"
                return 0
        return 1


    def checkVarNames(self, line):
        line = re.split("[,|\t]", line[:-1])
        for i in line:
            if not re.match("[A-Za-z]", i[0]):
                #raise FileError, "Enter a valid variable name"
                return 0
            for j in i[1:]:
                if not re.match("[A-Za-z0-9_]", j):
                    #raise FileError, "Enter a valid variable name"
                    return 0
        return 1


class ImportUserProvData():
    def __init__(self, name, filePath, varNames=[], varTypes=[], varNamesFileDummy=False, varTypesFileDummy=False):
        self.tableName = name

        self.filePath = os.path.realpath(filePath)
        self.filePath = self.filePath.replace("\\", "/")

        self.varNames = varNames
        self.varTypes = varTypes

        self.varNamesFileDummy = varNamesFileDummy
        self.varTypesFileDummy = varTypesFileDummy

        if len(varNames) == 0:
            self.varNamesDummy = False
        else:
            self.varNamesDummy = True
        if len(varTypes) == 0:
            self.varTypesDummy = False
        else:
            self.varTypesDummy = True

        self.createTableQuery()


    def createTableQuery(self):
        validVariableTypes = ['tinyint', 'smallint', 'mediumint', 'int','bigint',
                              'float', 'doubke',
                              'decimal',
                              'bit',
                              'char', 'varchar', 'text', 'binary', 'varbinary', 'blob', 'enum', 'set']
        self.query1 = ''
        self.query2 = ''

    #  creating a table query for the case when both varnames are variable type are specified
        with open(self.filePath, 'r') as f:
            if not self.varNamesDummy and self.varNamesFileDummy:
                self.varNames = f.readline()
                self.varNames = re.split("[,|\t]", self.varNames[:-1])

            if not self.varTypesDummy and self.varTypesFileDummy:
                self.varTypes = f.readline()
                self.varTypes = re.split("[,|\t]", self.varTypes[:-1])

            firstrow = f.readline()
            firstrow = re.split("[,|\t]", firstrow[:-1])

        for i in self.varNames:
            if not re.match("[A-Za-z]", i[0]):
                raise FileError, "Enter a valid variable name"

        for i in self.varTypes:
            if not re.match("[A-Za-z]", i[0]):
                raise FileError, "Enter a valid variable type definition"
            try:
                validVariableTypes.index(i.lower())
            except:
                raise FileError, "Enter a valid variable type definition"

        if len(self.varNames) <> len(firstrow):
            pass #raise FileError, "Please enter the same number of variable names as columns in the data file."
        if self.varNamesDummy == False and self.varNamesFileDummy == False:
            for i in range(len(firstrow)):
                self.varNames.append('Var%s'%(i+1))

        if len(self.varTypes) <> len(firstrow):
            pass #raise FileError, "Please enter the same number of variable type definitions as columns in the data file."
        if self.varTypesDummy == False and self.varTypesFileDummy == False:
            for i in range(len(firstrow)):
                self.varTypes.append('text')

        for i in range(len(firstrow)):
            self.query1 = self.query1 + self.varNames[i] + ' ' + self.varTypes[i] + ', '

        if len(self.varNames) <> len(self.varTypes):
            raise FileError,  "Mismatch in the number of Variable Names and Variable Types"


        self.query1 = self.query1[:-2]
        self.query1 = 'create table %s('%(self.tableName) + self.query1 + ')'

        self.query2 = ("""load data local infile "%s" into table %s fields terminated by "," """
                       """lines terminated by "\n" ignore %s lines""" %(self.filePath,
                                                                        self.tableName,
                                                                        int(self.varNamesFileDummy) + int(self.varTypesFileDummy)))
if __name__ == "__main__":

    #for b in ['test', 'names', 'types', 'none']:
    #for b in ['test']:
    for b in ['names', 'none']:
        a = FileProperties("C:/PopSim/test/%s.dat" %b)
        print b
        print "Var Type Dummy:", a.varTypesDummy
        print a.varTypes
        print "Var Names Dummy:", a.varNamesDummy
        print a.varNames

        c = ImportUserProvData(b, "c:/PopSim/test/%s.dat" %b, a.varNames, a.varTypes, a.varNamesDummy, a.varTypesDummy)
        print c.query1
        print c.query2

        print "\n\n"

