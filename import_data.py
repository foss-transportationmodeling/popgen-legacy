# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from __future__ import with_statement

import os
import re
import sys

class FileError(Exception):
    pass


class FileProperties():
    def __init__(self, filePath):
        with open(filePath, 'r') as f:
            self.varNames = []
            self.varTypes = []

            firstline = f.readline()
            secondline = f.readline()

            if self.checkVarTypes(firstline):
                self.varTypesDummy = True
                firstline = firstline[:-1]
                firstline = firstline.replace("\"", "")
                firstline = firstline.replace("'", "")
	        firstline = firstline.replace("\r", "")
                self.varTypes = re.split("[,|\t]", firstline)
                self.varNamesDummy = False
            else:
                self.varTypesDummy = False
                if self.checkVarNames(firstline):
                    self.varNamesDummy = True
                    firstline = firstline[:-1]
                    firstline = firstline.replace("\"", "")
                    firstline = firstline.replace("'", "")
		    firstline = firstline.replace("\r", "")
                    self.varNames = re.split("[,|\t]", firstline)
                else:
                    self.varNamesDummy = False
                if self.checkVarTypes(secondline):
                    self.varTypesDummy = True
                    secondline = secondline[:-1]
                    secondline = secondline.replace("\"", "")
                    secondline = secondline.replace("'", "")
		    secondline = secondline.replace("\r", "")
                    self.varTypes = re.split("[,|\t]", secondline)
                else:
                    self.varTypesDummy = False

            if self.varNamesDummy and self.varTypesDummy:
                if len(self.varNames) <> len(self.varTypes):
                    raise FileError, "Mismatch in the number of Variable Names and Variable Types"

	    # Automatically identifying the variable types
	    if not self.varTypesDummy and self.varNamesDummy:	
	        #self.varTypesDummy = True
		self.varTypes = self.createVarTypes(secondline)
                if len(self.varNames) <> len(self.varTypes):
                    raise FileError, "Mismatch in the number of Variable Names and Variable Types"
		

    def createVarTypes(self, line):
        line = line.replace("\"", "")
        line = line.replace("'", "")
        line = line.replace("\r", "")
        line = re.split("[,|\t]", line[:-1])
	
	varTypes = []
	for field in line:
	    if re.match("[0-9]", field[0]):
	        numType = True
		textType = False
	    elif re.match("[a-zA-Z]", field[0]):
		numType = False
		textType = True
		varTypes.append('text')

	    if numType:
		try:
		    intVal = int(field)
		    varTypes.append('bigint')
		except ValueError, e:
		    floatVal = float(field)
		    varTypes.append('float(27)')
	#print 'LINE - ', line
	#print 'Variable Types', varTypes
	return varTypes	


    def checkVarTypes(self, line):

        validVariableTypes = ['tinyint', 'smallint', 'mediumint', 'int','bigint',
                              'float', 'double', 'float(27)',
                              'decimal',
                              'bit',
                              'char', 'varchar', 'text', 'binary', 'varbinary', 'blob', 'enum', 'set']
        line = line.replace("\"", "")
        line = line.replace("'", "")
        line = line.replace("\r", "")

        line = re.split("[,|\t]", line[:-1])

        for i in line:
            try:
                validVariableTypes.index(i.lower())
            except:
                return 0
        return 1


    def checkVarNames(self, line):
        line = line.replace("\"", "")
        line = line.replace("'", "")
        line = line.replace("\r","")
        line = re.split("[,|\t]", line[:-1])
        line = ['%s' %i for i in line]

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

        self.filePath = os.path.realpath('%s' %filePath)
        if sys.platform.startswith('win'):
            self.filePath = self.filePath.replace("\\", "/")

        #self.filePath = os.path.realpath('%s' %filePath)
        #self.filePath = self.filePath.replace("\\", "/")

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
                              'float', 'double', 'float(27)',
                              'decimal',
                              'bit',
                              'char', 'varchar', 'text', 'binary', 'varbinary', 'blob', 'enum', 'set']
        self.query1 = ''
        self.query2 = ''

    #  creating a table query for the case when both varnames are variable type are specified
        with open(self.filePath, 'r') as f:
            if not self.varNamesDummy and self.varNamesFileDummy:
                #print "read first line"
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

        #print len(self.varTypes)
        #print validVariableTypes
        for i in self.varTypes:
            #if not re.match("[A-Za-z()0-9]", i[0]):
            #    raise FileError, "Enter a valid variable type definition"
            try:
                name = i.lower().rstrip()
                validVariableTypes.index(name)
            except:
                raise FileError, "Enter a valid variable type definition"

        #print firstrow, len(firstrow)

        #print 'lenght of variable names',len(self.varNames)
        #print 'length of the first row', len(firstrow)

        if len(self.varNames) <> len(firstrow):
            raise FileError, "Enter the same number of variable names as columns in the data file."

        if self.varNamesDummy == False and self.varNamesFileDummy == False:
            for i in range(len(firstrow)):
                self.varNames.append('Var%s'%(i+1))

        if len(self.varTypes) <> len(firstrow):
            raise FileError, "Enter the same number of variable type definitions as columns in the data file."

        if self.varTypesDummy == False and self.varTypesFileDummy == False:
            for i in range(len(firstrow)):
                self.varTypes.append('text')

        for i in range(len(firstrow)):
            self.query1 = self.query1 + self.varNames[i] + ' ' + self.varTypes[i] + ', '

        if len(self.varNames) <> len(self.varTypes):
            raise FileError,  "Mismatch in the number of Variable Names and Variable Types"


        self.query1 = self.query1[:-2]
        self.query1 = 'create table %s('%(self.tableName) + self.query1 + ')'

        if (re.split("[.]", self.filePath)[-1] == 'csv' or re.split("[.]", self.filePath)[-1] == 'uf3' or
            re.split("[.]", self.filePath)[-1] == 'txt'):
            
            self.query2 = ("""load data local infile "%s" into table %s fields terminated by "," """
                           """lines terminated by "\\n" ignore %s lines""" %(self.filePath,
                                                                              self.tableName,
                                                                              int(self.varNamesFileDummy) + int(self.varTypesFileDummy)))
        if re.split("[.]", self.filePath)[-1] == 'dat':
            self.query2 = ("""load data local infile "%s" into table %s fields terminated by "\t" """
                           """lines terminated by "\\n" ignore %s lines""" %(self.filePath,
                                                                              self.tableName,
                                                                              int(self.varNamesFileDummy) + int(self.varTypesFileDummy)))

if __name__ == "__main__":

    #for b in ['test', 'names', 'types', 'none']:
    #for b in ['test']:
    for b in ['names']:
        a = FileProperties("/home/kkonduri/simtravel/test/bmc_taz/hhld_marginals.csv")
        print "Var Type Dummy:", a.varTypesDummy, "Var Names Dummy:", a.varNamesDummy
        print a.varTypes
        print a.varNames


        a = FileProperties("/home/kkonduri/simtravel/test/bmc_taz/geocorr.csv")
        print "Var Type Dummy:", a.varTypesDummy, "Var Names Dummy:", a.varNamesDummy
        print a.varTypes 
	print a.varNames

