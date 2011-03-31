# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2010, Arizona State University
# See PopGen/License

import os
import MySQLdb

from numpy import array, zeros, unique, histogram
from numpy import fix as quo

class SaveSyntheticPopFile():
    def __init__(self, project, persNameTable=None, housingNameTable=None):
        self.project = project

        self.fileType = 'dat'
        self.fileSep = '\t'

	if persNameTable is not None:
	    self.personName = persNameTable.name
	    self.personLocation = persNameTable.location
	else:
	    self.personName = 'person_synthetic_data'
	    self.personLocation = self.project.location

	if housingNameTable is not None:
	    self.housingName = housingNameTable.name
	    self.housingLocation = housingNameTable.location
	else:
	    self.housingName = 'housing_synthetic_data'
	    self.housingLocation = self.project.location


        self.gqAnalyzed = self.isGqAnalyzed()
        self.persAnalyzed = self.isPersonAnalyzed()
	
	self.uniqueIds = True

    def isGqAnalyzed(self):
        if not self.project.gqVars:
            return False

        if self.project.sampleUserProv.userProv == False and self.project.controlUserProv.userProv == False:
            return True

        if self.project.sampleUserProv.userProv == True and self.project.sampleUserProv.gqLocation <> "":
            return True

        if self.project.controlUserProv.userProv == True and self.project.controlUserProv.gqLocation <> "":
            return True


        return False


    def isPersonAnalyzed(self):
        if not self.project.selVariableDicts.persControl:
            return False

        if self.project.sampleUserProv.userProv == False and self.project.controlUserProv.userProv == False:
            return True

        if self.project.sampleUserProv.userProv == True and self.project.sampleUserProv.personLocation <> "":
            return True

        if self.project.controlUserProv.userProv == True and self.project.controlUserProv.personLocation <> "":
            return True



        return False

    def execute_query(self, query):
	db = MySQLdb.connect(user= '%s' %self.project.db.username,
                             passwd = '%s' %self.project.db.password, 
			     db = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario))
	dbc = db.cursor()
	
	try:
	    dbc.execute(query)
	    results = dbc.fetchall()
	
	except MySQLdb.Error, e:
	    print 'Error executing query - %s and error is - %s' %(query, e)
	    results = None	

	dbc.close()
	db.commit()
	return results


    def save(self):

        filename = '%s/%s.%s' %(self.housingLocation, self.housingName, self.fileType)

	check = 1

        if check == 1:
	    try:
                os.remove(filename)
	    except Exception, e:
		print 'Error while deleting file - %s and error is - %s' %(filename, e)

            hhldVariablesDict, hhldVariables = self.getVariables('hhld_sample')
            hhldVariablesDict = self.deleteDictEntries(hhldVariablesDict)
            #hhldSelVariables = self.getSelectedVariables(hhldVariablesDict, self.project.hhldVars, 
            #                                             "Select Household Variables to Add to Synthetic Data")
	   
	    hhldSelVariables = hhldVariablesDict.keys()

            hhldvarstr = ","
            if hhldSelVariables is not None:
                for  i in hhldSelVariables:
                    hhldvarstr = hhldvarstr + '%s,' %i
                hhldvarstr = hhldvarstr[:-1]
            else:
                hhldvarstr = ""
                QMessageBox.warning(self, "Export Synthetic Population Tables", 
                                    """No household variables selected for exporting""", QMessageBox.Ok)                


            self.execute_query("""drop table temphou1""")
            self.execute_query("""create table temphou1 select housing_synthetic_data.* %s from housing_synthetic_data"""
                               """ left join hhld_sample using (state, serialno)""" %(hhldvarstr))
            self.execute_query("""alter table temphou1 drop column hhuniqueid""")
            self.execute_query("""alter table temphou1 add index(state, serialno)""")


            if self.project.gqVars:
                gqVariablesDict, gqVariables = self.getVariables('gq_sample')
                gqVariablesDict = self.deleteDictEntries(gqVariablesDict)

	        #gqSelVariables = self.getSelectedVariables(gqVariablesDict, self.project.gqVars, 
                #                                         "Select Groupquarter Variables to Add to Synthetic Data")
		
		gqSelVariables = gqVariablesDict.keys()


                gqvarstr = ","
                if gqSelVariables is not None:
                    for  i in gqSelVariables:
                        gqvarstr = gqvarstr + '%s,' %i
                    gqvarstr = gqvarstr[:-1]
                else:
                    gqvarstr = ""
                    QMessageBox.warning(self, "Export Synthetic Population Tables", 
                                        """No groupquarter variables selected for exporting""", QMessageBox.Ok)          
                  
                self.execute_query("""drop table temphou2""")
                self.execute_query("""create table temphou2 select temphou1.* %s from temphou1"""
                                   """ left join gq_sample using (state, serialno)""" %(gqvarstr))
            else:
                self.execute_query("""alter table temphou1 rename to temphou2""")

	    if 1:
  	        self.execute_query("""alter table temphou2 drop column serialno""")
  	        self.execute_query("""alter table temphou2 drop column tract""")
		self.execute_query("""alter table temphou2 change bg taz bigint""")

                housingSynTableVarDict, housingSynTableVars = self.getVariables('temphou2')

		housingVarStr = ''

		for var in housingSynTableVars:
		    housingVarStr += "%s," %var
		housingVarStr = housingVarStr[:-1]


                if self.uniqueIds is None:
                    #print ("""select * from temphou2 into outfile """
                    #       """'%s/housing_synthetic_data.%s' fields terminated by '%s'"""
                    #       %(self.folder, self.fileType, self.fileSep))
                    self.execute_query("""select * from temphou2 into outfile """
                                       """'%s/%s.%s' fields terminated by '%s'"""
                                       %(self.housingLocation, self.housingName, self.fileType, self.fileSep))

                else:

                    self.execute_query("""create table if not exists temphou_unique select * from temphou2 where 0""")

                    self.execute_query("""delete from temphou_unique""")

                    results = self.execute_query("""select * from temphou2""")

		    if results is not None:
			cols = len(results[0])

		    indexOfFrequency = housingSynTableVars.index('frequency')
		
                    fileRef = open("%s/%s.%s" %(self.housingLocation, self.housingName, self.fileType), 'w')

                    colIndices = range(cols)
		    for rec in results:
			freq = rec[indexOfFrequency]
			cols = []
	                for i in rec:
			    cols.append('%s' %i)
			    cols.append(self.fileSep)

		    	for i in range(freq):
			    cols[indexOfFrequency*2] = '%s' %(i+1)
			    fileRef.write(''.join(cols[:-1]))
			    fileRef.write('\n')
		    fileRef.close()



		    """
                    while query.next():
                        freq = query.value(indexOfFrequency).toInt()[0]
                        cols = []

                        for i in colIndices:
                            cols.append('%s' %query.value(i).toString())
                            cols.append(self.fileSep)
                            
                        for i in range(freq):
                            cols[indexOfFrequency*2] = '%s' %(i+1)
                            fileRef.write(''.join(cols[:-1]))
                            fileRef.write('\n')
                    fileRef.close()
                    """
        
                    self.execute_query("""load data local infile '%s/%s.%s' into table temphou_unique """\
                                           """fields terminated by '%s' (%s)""" %(self.housingLocation, self.housingName, 
									     self.fileType, self.fileSep,
									     housingVarStr))
                        
            
            self.storeMetaData(housingSynTableVars, self.housingLocation, self.housingName)
            
            self.execute_query("""drop table temphou1""")

            if not self.project.gqVars:
                self.execute_query("""drop table temphou2""")

        filename = '%s/%s.%s' %(self.personLocation, self.personName, self.fileType)
	check = 1

        if check  == 1:

	    try:
                os.remove(filename)
	    except Exception, e:
		print 'Error while deleting file - %s and error is - %s' %(filename, e)

            personVariablesDict, personVariables = self.getVariables('person_sample')
            personVariablesDict = self.deleteDictEntries(personVariablesDict)
            if self.project.personVars is None:
                personVarsList = []
            else:
                personVarsList = self.project.personVars


            #personSelVariables = self.getSelectedVariables(personVariablesDict, personVarsList, 
            #                                               "Select Person Variables to Add to Synthetic Data")
	
	    personSelVariables = personVariablesDict.keys()

            personvarstr = ","
            if personSelVariables is not None:
                for  i in personSelVariables:
                    personvarstr = personvarstr + '%s,' %i
                personvarstr = personvarstr[:-1]
            else:
                personvarstr = ""
                QMessageBox.warning(self, "Export Synthetic Population Tables", 
                                    """No person variables selected for exporting""", QMessageBox.Ok)                
            
            self.execute_query("""drop table tempperson""")
            self.execute_query("""create table tempperson select person_synthetic_data.* %s from person_synthetic_data"""
                               """ left join person_sample using (state, serialno, pnum)""" %(personvarstr))
            self.execute_query("""alter table tempperson drop column personuniqueid""")

            if 1:
  	        self.execute_query("""alter table tempperson drop column serialno""")
  	        self.execute_query("""alter table tempperson drop column tract""")
		self.execute_query("""alter table tempperson change bg taz bigint""")


                personSynTableVarDict, personSynTableVars = self.getVariables('tempperson')
	
		personVarStr = ''

		for var in personSynTableVars:
		    personVarStr += "%s," %var
		personVarStr = personVarStr[:-1]

                if self.uniqueIds is None:

                    self.execute_query("""select * from tempperson into outfile """
                                       """'%s/%s.%s' fields terminated by '%s'"""
                                       %(self.personLocation, self.personName, self.fileType, self.fileSep))
                  

                else:

                    self.execute_query("""create table if not exists tempperson_unique select * from tempperson where 0""")

                    self.execute_query("""delete from tempperson_unique""")

                    results = self.execute_query("""select * from tempperson""")


		    if results is not None:
			cols = len(results[0])

		    indexOfFrequency = housingSynTableVars.index('frequency')
		
                    fileRef = open("%s/%s.%s" %(self.personLocation, self.personName, self.fileType), 'w')

                    colIndices = range(cols)
		    for rec in results:
			freq = rec[indexOfFrequency]
			cols = []
	                for i in rec:
			    cols.append('%s' %i)
			    cols.append(self.fileSep)

		    	for i in range(freq):
			    cols[indexOfFrequency*2] = '%s' %(i+1)
			    fileRef.write(''.join(cols[:-1]))
			    fileRef.write('\n')
		    fileRef.close()

      
                    self.execute_query("""load data local infile '%s/%s.%s' into table tempperson_unique """\
                                           """fields terminated by '%s' (%s)""" %(self.personLocation, self.personName, 
										  self.fileType, self.fileSep,
										  personVarStr))
                        
            self.storeMetaData(personSynTableVars, self.personLocation, self.personName)


    def deleteDictEntries(self, dict):
        vars = ['state', 'pumano', 'hhid', 'serialno', 'pnum', 'hhlduniqueid', 'gquniqueid', 'personuniqueid']
        for i in vars:
            try:
                dict.pop(i)
            except:
                pass
        return dict


    def storeMetaData(self, varNames, location, tablename):
        f = open('%s/%s_meta.txt' %(location, tablename), 'w')
        col = 1
        for i in varNames:
            f.write('column %s -  %s\n' %(col, i))
            col = col + 1
        f.close()


    def getVariables(self, tablename):
	results = self.execute_query("""desc %s""" %(tablename))
        
        varDict = {}
        varNameList = []

	for row in results:
	   varname = row[0]
	   varDict[varname] = ""
	   varNameList.append(varname)

        return varDict, varNameList
        
    
class ExportSummaryFile(SaveSyntheticPopFile):
    def __init__(self, project, summaryTableNameLoc):
        SaveSyntheticPopFile.__init__(self, project)
	self.name = summaryTableNameLoc.name
	
	if summaryTableNameLoc.location == "":
	    self.location = self.project.location
	else:
            self.location = summaryTableNameLoc.location


    def save(self):

	filename = '%s/%s.%s'%(self.location, self.name, self.fileType)


	check = 1
        if check == 1:

	    try:
                os.remove(filename)
	    except Exception, e:
		print 'Error while deleting file - %s and error is - %s' %(filename, e)

            self.createSummaryTables('housing')
            self.createSummaryTables('person')

            varCorrDict = {}
            varCorrDict.update(self.variableControlCorrDict(self.project.selVariableDicts.hhld))
            varCorrDict.update(self.variableControlCorrDict(self.project.selVariableDicts.gq))

            self.createHousingMarginalsTable(varCorrDict.values())

            varCorrDict = self.variableControlCorrDict(self.project.selVariableDicts.person)

            self.createMarginalsTable(varCorrDict.values())

            self.createGivenControlTotalColumns(self.project.selVariableDicts.hhld)
            if self.isGqAnalyzed:
                self.createGivenControlTotalColumns(self.project.selVariableDicts.gq)
            if self.isPersonAnalyzed:
                self.createGivenControlTotalColumns(self.project.selVariableDicts.person)

            self.createMarginalsSummaryTable()
	    self.appendPerformanceStatistics()
        

	    self.execute_query("""alter table geo_perf_summary drop column tract""")
	    self.execute_query("""alter table geo_perf_summary change bg taz bigint""")

            self.execute_query("""select * from geo_perf_summary into outfile """
                               """'%s/%s.%s' fields terminated by '%s'""" %(self.location, self.name, 
									    self.fileType, self.fileSep))

            summaryTableVarDict, summaryTableVars = self.getVariables('geo_perf_summary')
            self.storeMetaData(summaryTableVars, self.location, self.name)



    def createSummaryTables(self, synthesisType):
        
        self.execute_query("""drop table %s_summary """%(synthesisType))

        self.execute_query("""create table %s_summary """
                           """select state, county, tract, bg, sum(frequency) as %s_syn_sum from %s_synthetic_data """
                           """group by state, county, tract, bg""" %(synthesisType, synthesisType, synthesisType))


    def createHousingMarginalsTable(self, housingVars):
        dummy = ''
        for i in housingVars:
            dummy = dummy + i + ','
        dummy = dummy[:-1]

        self.execute_query("""drop table housing_marginals""")        


        self.execute_query("""alter table hhld_marginals add index(state, county, tract, bg)""")

        if self.gqAnalyzed:
            self.execute_query("""alter table gq_marginals add index(state, county, tract, bg)""")
            

            self.execute_query("""create table housing_marginals select state, county, tract, bg, %s """
                               """ from hhld_marginals left join gq_marginals using(state, county, tract, bg)"""
                               %dummy)
        else:
            self.execute_query("""create table housing_marginals select * from hhld_marginals """)


    def createMarginalsTable(self, persVars):
        dummy = ''
        for i in persVars:
            dummy = dummy + i + ','
        dummy = dummy[:-1]

        self.execute_query("""drop table marginals""")

        self.execute_query("""alter table housing_marginals add index(state, county, tract, bg)""")

        if self.persAnalyzed:        
            self.execute_query("""alter table person_marginals add index(state, county, tract, bg)""")
    
            self.execute_query("""create table marginals select housing_marginals.*, %s """
                               """ from housing_marginals left join person_marginals using(state, county, tract, bg)"""
                               %dummy)
        else:
            self.execute_query("""create table marginals select * from housing_marginals""")
            

    def createMarginalsSummaryTable(self):
        self.execute_query("""alter table marginals add index(state, county, tract, bg)""")

        self.execute_query("""alter table housing_summary add index(state, county, tract, bg)""")

        self.execute_query("""alter table person_summary add index(state, county, tract, bg)""")

        self.execute_query("""drop table summary""")

        self.execute_query("""drop table comparison""")

        self.execute_query("""create table summary select housing_summary.*, person_syn_sum """
                           """ from housing_summary left join person_summary using(state, county,tract, bg)""")

        self.execute_query("""create table comparison select marginals.*, housing_syn_sum, person_syn_sum """
                           """ from marginals left join summary using(state, county,tract, bg)""")


    def appendPerformanceStatistics(self):
        self.execute_query("""drop table geo_perf_summary""")

	self.execute_query("""create table geo_perf_summary select comparison.*, chivalue, pvalue, synpopiter, heuriter, aardvalue """
                           """ from comparison left join performance_statistics using(state, county,tract, bg)""")

        
    def variableControlCorrDict(self, vardict):
        varCorrDict = {}
        vars = vardict.keys()
        for i in vars:
            for j in vardict[i].keys():
                cat = (('%s' %j).split())[-1]
                varCorrDict['%s%s' %(i, cat)] = '%s' %vardict[i][j]
        return varCorrDict

    def createGivenControlTotalColumns(self, varDict):
        for i in varDict.keys():
            self.execute_query("""alter table marginals add column %s_act_sum int"""
                               %(i))

            updateString = ''
            for j in varDict[i].keys():
                updateString = updateString + varDict[i][j] + "+"
            updateString = updateString[:-1]
                
            self.execute_query("""update marginals set %s_act_sum = %s"""
                               %(i, updateString))


            for j in varDict[i].keys():
                self.execute_query("""alter table marginals drop %s"""
                                   %(varDict[i][j]))
                
class ExportMultiwayTables(SaveSyntheticPopFile):
    def __init__(self, project, mwayTable):
        SaveSyntheticPopFile.__init__(self, project)
	self.name = mwayTable.nameLoc.name
	
	if mwayTable.nameLoc.location == "":
	    self.location = self.project.location
	else:
            self.location = mwayTable.nameLoc.location

	if mwayTable.tableName == 'housing_synthetic':
	    self.tableFrom = 'temphou_unique'
	elif mywayTable.tableName == 'person_synthetic':
	    self.tableFrom = 'tempperson_unique'
	
	self.varList = mwayTable.varList


    def saveMultiwayTables(self):
		
	self.save()

	filename = '%s/%s.%s'%(self.location, self.name, self.fileType)


	check = 1
        if check == 1:

	    try:
                os.remove(filename)
	    except Exception, e:
		print 'Error while deleting file - %s and error is - %s' %(filename, e)

	multiWayEntries = self.createMultiWayTables()
        fileRef = open("%s/%s.%s" %(self.location, self.name, self.fileType), 'w')
	
	cols = multiWayEntries.shape[-1]
	
	colIndicesVars = range(cols)[1:-1]

	allControlVars = self.project.hhldVars + self.project.gqVars + self.project.personVars
	
	allControlDims = list(self.project.hhldDims) + list(self.project.gqDims) + list(self.project.personDims)

	multiWayDims = [allControlDims[allControlVars.index(var)] for var in self.varList]

	#print allControlVars
	#print allControlDims

	tazIdsUnique, tazIds_reverse_indices = unique(multiWayEntries[:,0], return_inverse=True)
	
        binsIndices = array(range(tazIds_reverse_indices.max()+2))
        histIndices = histogram(tazIds_reverse_indices, bins=binsIndices)

	#print tazIdsUnique
	#print histIndices

	indicesRowCount = histIndices[0]
	indicesRowCumSum = indicesRowCount.cumsum()

	indices = zeros((tazIdsUnique.shape[0], 3), int)
	
	indices[:,0] = tazIdsUnique
	indices[1:, 1] = indicesRowCumSum[:-1]
	indices[:, 2] = indicesRowCumSum
	
	#print 'Indices', indices
	
	catIndex = self.numBreakDown(array(multiWayDims))


	#print catIndex
        fileRef = open("%s" %(filename), 'w')
	# Printing multiway tables
	for i in indices:

 	    catIndexValDict = {}
	    for cat in catIndex:
	        catIndexValDict[tuple(cat)] = 0

	    tazId = i[0]
		
	    firstRowInd = i[1]
	    LastRowInd = i[2]
	    corrMultiWayRows = multiWayEntries[firstRowInd:LastRowInd]
	
	    print 'TAZ ID - ', tazId
	    print 'Corresponding Rows'
	    print corrMultiWayRows	

	    for rec in corrMultiWayRows:
		catFrmDb = tuple(rec[1:1+len(self.varList)])
		catIndexValDict[catFrmDb] = rec[-1]
		

	    # Writing to the flat file

	    strToWrite='%s\t' %tazId

	    for cat in catIndex:
		strToWrite += '%s\t' %catIndexValDict[tuple(cat)]
		
	    strToWrite = strToWrite[:-1] + '\n'

	    print strToWrite
	    
	    fileRef.write(strToWrite)	
        fileRef.close()
	#fullMultiWayIndex = zeros((multiWayDims))
	
	
		
    def numBreakDown(self, dimensions):
    	"""This method breaksdown the cell number 'n' into its index wrt to the
	   categories defined by 'm' """
    	index_array = []

    	table_size = dimensions.cumprod()[-1]
    	composite_index = range(table_size)
# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2010, Arizona State University
# See PopGen/License

    	for j in composite_index:
    	    n = j
    	    index = []
    	    for i in reversed(dimensions):
            	quotient = quo(n/i)
            	remainder = n - quotient * i
            	n = quotient
            	index.append(remainder+1)
            index.reverse()
            index_array.append(index)
    	return index_array		



    def createMultiWayTables(self):
	varGrpByStr = ''
	varCondStr = ''
	for var in self.varList:
	    varGrpByStr += '%s,' %var
	    varCondStr += '%s<>0 and ' %var
	varGrpByStr = varGrpByStr[:-1]
	varCondStr = varCondStr[:-4]
        self.execute_query("""drop table %s""" %self.name)

	results = self.execute_query("""select taz, %s, count(*) from %s where %s group by taz, %s""" 
			   	     %(varGrpByStr, self.tableFrom, varCondStr, varGrpByStr))
	return array(results)
	












































