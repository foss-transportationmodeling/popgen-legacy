# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2010, Arizona State University
# See PopGen/License

import re
import os
import copy
import MySQLdb
from lxml import etree
from numpy import array, asarray
from collections import defaultdict
from newproject import *


class ConfigParser(object):
    def __init__(self, configObject):
        if not isinstance(configObject, etree._ElementTree):
            print ConfigurationError, """The configuration object input is not a valid """\
                """etree.Element object. Trying to load the object from the configuration"""\
                """ file."""

        self.configObject = configObject

    def parse_skip(self):
        runElement = self.configObject.find('Skip')

        if runElement is None:
            return False

        runValue = runElement.get('run')

        if runValue == 'True':
            return True
        else:
            return False


    def parse_project(self):

        projectElement = self.configObject.find('Project')
        name, loc = self.parse_project_attribs(projectElement)

        dbInfoObject = self.parse_database_attribs()

        inputElement = self.configObject.find('Inputs')
        
        createTables = inputElement.get('create')
        if createTables == 'True':
            createTables = True
        if createTables == 'False':
            createTables = False

        
        geocorrObj = self.parse_geocorr_input(inputElement)
        sampleObj = self.parse_sample_input(inputElement)
        controlObj = self.parse_control_input(inputElement)



        self.project = NewProjectPopGenCore()
        # Project Attribs
        self.project.name = name
        self.project.location = loc

        # Resolution
        self.project.resolution = 'TAZ'

        self.project.db = dbInfoObject
        self.project.geocorrUserProv = geocorrObj
        self.project.sampleUserProv = sampleObj
        self.project.controlUserProv = controlObj
        self.project.createTables = createTables

    def parse_scenarios(self):

        scenarioIterator = self.configObject.getiterator('Scenario')
        self.scenarioList = []

        for scenarioElement in scenarioIterator:
            scenarioProjObj = copy.deepcopy(self.project)
            self.parse_scenario(scenarioProjObj, scenarioElement)
            self.scenarioList.append(scenarioProjObj)

    def parse_project_attribs(self, projectElement):
        name = projectElement.get('name')
        loc = projectElement.get('location')

        return name, loc

    def parse_database_attribs(self):
        db_element = self.configObject.find('DBConfig')
        driver = db_element.get('dbprotocol')
        hostname = db_element.get('dbhost')
        username = db_element.get('dbusername')
        password = db_element.get('dbpassword')

        dbInfoObject = DBInfo(hostname, username, 
                              password)
        print dbInfoObject
        return dbInfoObject


    def parse_geocorr_input(self, inputElement):
        geoElement = inputElement.find('GeographicCorrespondence')
        geoLoc = self.return_loc(geoElement)
        
        geoObj = Geocorr(True, geoLoc)
        print geoObj
        return geoObj

    def parse_sample_input(self, inputElement):
        hhldElement = inputElement.find('HouseholdSample')
        hhldLoc = self.return_loc(hhldElement)

        gqElement = inputElement.find('GQSample')
        gqLoc = self.return_loc(gqElement)        

        persElement = inputElement.find('PersonSample')
        persLoc = self.return_loc(persElement)

        sampleObj = Sample(True, sampleHHLocation = hhldLoc, 
                           sampleGQLocation = gqLoc, 
                           samplePersonLocation = persLoc)
        print sampleObj
        return sampleObj

    def parse_control_input(self, inputElement):
        hhldElement = inputElement.find('HouseholdControl')
        hhldLoc = self.return_loc(hhldElement)

        gqElement = inputElement.find('GQControl')
        gqLoc = self.return_loc(gqElement)        

        persElement = inputElement.find('PersonControl')
        persLoc = self.return_loc(persElement)

        controlObj = Control(True, controlHHLocation = hhldLoc, 
                                controlGQLocation = gqLoc, 
                                controlPersonLocation = persLoc)
        print controlObj
        return controlObj





    def return_loc(self, locElement):
        loc = ""
        if locElement is not None:
            loc = locElement.get('location')
        return loc

    def parse_scenario(self, scenarioProjObj, scenarioElement):
        scenario, description = self.parse_scenario_attribs(scenarioElement)

	scenarioProjObj.scenario = scenario
	scenarioProjObj.description = description
        scenarioProjObj.filename = scenarioProjObj.name + 'scenario' + scenario

        #Checking to see if data needs to be prepared
        prepareData = scenarioElement.get('prepare_data')
        if prepareData == 'True':
            scenarioProjObj.prepareData = True
        if prepareData == 'False':
            scenarioProjObj.prepareData = False


        run = scenarioElement.get('run')
        if run == 'True':
            scenarioProjObj.run = True
        if run == 'False':
            scenarioProjObj.run = False


        # Parsing control variables and number of dimensions
        controlVarsElement = scenarioElement.find('ControlVariables')
        hhldVars, hhldDims = self.parse_control_variables(controlVarsElement, 'Household')
        scenarioProjObj.hhldVars = hhldVars
        scenarioProjObj.hhldDims = hhldDims

        gqVars, gqDims = self.parse_control_variables(controlVarsElement, 'GroupQuarter')
        scenarioProjObj.gqVars = gqVars
        scenarioProjObj.gqDims = gqDims

        personVars, personDims = self.parse_control_variables(controlVarsElement, 'Person')
        scenarioProjObj.personVars = personVars
        scenarioProjObj.personDims = personDims

	personControlElement = controlVarsElement.find('Person')
	isPersonControlled = personControlElement.get('control')	
	if isPersonControlled == 'False':
	    scenarioProjObj.selVariableDicts.persControl = False
	else:
	    scenarioProjObj.selVariableDicts.persControl = True	

	# Parsing household marginal adjustment to account for 
	# person total inconsistency
	margAdjElement = scenarioElement.find('AdjustHouseholdMarginals')
	if margAdjElement is not None:
            modify = margAdjElement.get('modify')
	    if modify == 'True':
	        scenarioProjObj.selVariableDicts.hhldMargsModify = True
                hhldSizeVar, aveHhldSize, refPersVar = self.parse_modified_marginals(margAdjElement)
                scenarioProjObj.selVariableDicts.hhldSizeVarName = hhldSizeVar
                scenarioProjObj.selVariableDicts.aveHhldSizeLastCat = aveHhldSize
                scenarioProjObj.selVariableDicts.refPersName = refPersVar
	    else:
		scenarioProjObj.selVariableDicts.hhldMargsModify = False

        # Parsing correspondence mapping
        varMapElement = scenarioElement.find('CorrespondenceMap')
        hhldDict = self.parse_correspondence_map(varMapElement, 'Household')
        scenarioProjObj.selVariableDicts.hhld = hhldDict

        gqDict = self.parse_correspondence_map(varMapElement, 'GroupQuarter')
        scenarioProjObj.selVariableDicts.gq = gqDict

        personDict = self.parse_correspondence_map(varMapElement, 'Person')
        scenarioProjObj.selVariableDicts.person = personDict

        parameterElement = scenarioElement.find('Parameters')
        parameterObj = self.parse_parameters(parameterElement)
        scenarioProjObj.parameters = parameterObj

        adjustMargElement = scenarioElement.find('ModifiedMarginals')
	if adjustMargElement is not None:
            modify = adjustMargElement.get('modify')
            if modify == 'True':
                adjMargs = self.parse_adjust_marginals(adjustMargElement)
                scenarioProjObj.adjControlsDicts.hhld = adjMargs
                scenarioProjObj.adjControlsDicts.gq = adjMargs
                scenarioProjObj.adjControlsDicts.person = adjMargs

        geogListElement = scenarioElement.find('SynthesizeGeographies')
        geogObjList = self.parse_geographies(geogListElement)
        print '\tNumber of geographies identified for synthesis - ', len(geogObjList)
        self.stateList = self.retrieve_state_list(geogObjList)
        scenarioProjObj.synthesizeGeoIds = geogObjList


	outputElement = scenarioElement.find('Outputs')
	scenarioProjObj.multiwayTableList = self.parse_multiway_tables(outputElement)
	(scenarioProjObj.summaryTableExport, 
	 scenarioProjObj.summaryTableNameLoc) = self.parse_summary_table(outputElement)
	(scenarioProjObj.synTableExport, 
	 scenarioProjObj.synPersTableNameLoc,
	 scenarioProjObj.synHousingTableNameLoc) = self.parse_synthetic_population_tables(outputElement)


    def retrieve_state_list(self, geogObjList):
        stateList = []
        for geogObj in geogObjList:
            stateList.append(geogObj.state)
        return list(set(stateList))

    def parse_scenario_attribs(self, scenarioElement):
        scenario = scenarioElement.get('value')
        description = scenarioElement.get('description')

        return scenario, description


    def parse_control_variables(self, controlVarsElement, controlType):
        controlTypeElement = controlVarsElement.find(controlType)

	variables = []
        variableDict = {}
        orderOfVars = []
	varsOrderDict = {}
        varsIterator = controlTypeElement.getiterator('Variable')
        for varElement in varsIterator:
            controlVar = varElement.get('control')
            if controlVar <> 'True':
                continue
            name = varElement.get('name')
	    order = varElement.get('order')
	    if order is not None:
		orderOfVars.append(order)
	        varsOrderDict[order] = name
            numCats = int(varElement.get('num_categories'))
            variableDict[name] = numCats


	orderOfVars.sort()
	for i in range(len(orderOfVars)):
	    variables.append(varsOrderDict[orderOfVars[i]])

	
        otherVariables = variableDict.keys()
	otherVariables.sort()
	
	for var in otherVariables:
	    if var in variables:
		continue
	    else:
		variables.append(var)

	variableDims = [variableDict[var] for var in variables]

        print 'For %s' %(controlType)
        print '\tCONTROL VARIABLES:%s' %(variables)
        print '\tCONTROL VARIABLE DIMENSIONS:%s\n' %(variableDims)
        return variables, array(variableDims)
            

    def parse_correspondence_map(self, varMapElement, controlType):
        varMapTypeElement = varMapElement.find(controlType)

        varMapDict = defaultdict(dict)
        
        varMapIterator = varMapTypeElement.getiterator('ControlVariableMap')
        for varMap in varMapIterator:
            var = varMap.get('name')
            value = varMap.get('category')
            margVar = varMap.get('marginal_variable')

            varMapDict[var]['%s, Category %s' %(var, value)] = margVar

        print 'CORRESPONDENCE MAP for %s:' %(controlType)
        for i in varMapDict.keys():
            print '\t %s --> %s' %(i, varMapDict[i])
        print
        return varMapDict


    def parse_parameters(self, parameterElement):
        ipfTolElement = parameterElement.find('IPFTolerance')
        ipfTol = float(ipfTolElement.get('value'))

        ipfItersElement = parameterElement.find('IPFIterations')
        ipfIters = int(ipfItersElement.get('value'))

        ipuTolElement = parameterElement.find('IPUTolerance')
        ipuTol = float(ipuTolElement.get('value'))

        ipuItersElement = parameterElement.find('IPUIterations')
        ipuIters = int(ipuItersElement.get('value'))


        synDrawsTolElement = parameterElement.find('SyntheticDrawsTolerance')
        synDrawsTol = float(synDrawsTolElement.get('value'))

        synDrawsItersElement = parameterElement.find('SyntheticDrawsIterations')
        synDrawsIters = int(synDrawsItersElement.get('value'))
        
        roundingProcElement = parameterElement.find('RoundingProcedure')
        roundingProc = roundingProcElement.get('name')

        parameterObj = Parameters(ipfTol, ipfIters,
                                  ipuTol, ipuIters,
                                  synDrawsIters, synDrawsTol,
                                  roundingProc)
        print parameterObj
        return parameterObj



    def parse_modified_marginals(self, modifiedMargElement):
	hhldSizeVarElement = modifiedMargElement.find('HouseholdSize')
	hhldSizeVar = hhldSizeVarElement.get('name')
	
	aveHhldSizeLastCatElement = modifiedMargElement.find('AverageHouseholdSizeLastCategory')
	aveHhldSizeLastCat = float(aveHhldSizeLastCatElement.get('value'))
	
	refPersonVarElement = modifiedMargElement.find('ReferencePersonTotalVariable')
	refPersonVar = refPersonVarElement.get('name')

	#print hhldSizeVar, aveHhldSizeLastCat, refPersonVar
	return hhldSizeVar, aveHhldSizeLastCat, refPersonVar

    def parse_adjust_marginals(self, adjustMargElement):
        # To address person total inconsistency
	adjDict = defaultdict(dict)
	geoIdIterator = adjustMargElement.getiterator('GeoId')

	for geoIdElement in geoIdIterator:
	    adjDict.update(self.parse_geo_modified_marginals(geoIdElement))

	return adjDict


    def parse_geo_modified_marginals(self, geoIdElement):
	print 'ADJUSTED MARGINALS FOR SELECTED GEOGRAPHIES'
	adjDict = defaultdict(dict)
	state = geoIdElement.get('state')
	county = geoIdElement.get('county')
	tract = 1
	bg = geoIdElement.get('taz')
	geoStr = '%s,%s,%s,%s' %(state, county, tract, bg)

	varIterator = geoIdElement.getiterator('Variable')

	for varElement in varIterator:
	    var = varElement.get('name')
	    oldMarginalList, newMarginalList = self.parse_new_old_marginal(varElement)
	    adjDict[geoStr][var] = [oldMarginalList, newMarginalList]
	print '\t', adjDict
	return adjDict
	

    def parse_new_old_marginal(self, varElement):
	catIterator = varElement.getiterator('Category')
	oldMarginalList = []
	newMarginalList = []
	for catElement in catIterator:
	    cat = catElement.get('value')
	    oldMarginal = float(catElement.get('old_marginal'))
	    newMarginal = float(catElement.get('new_marginal'))

	    oldMarginalList.append(oldMarginal)
	    newMarginalList.append(newMarginal)
	return oldMarginalList, newMarginalList

    def parse_geographies(self, geogListElement):
        print 
        checkFullRegionElement = geogListElement.get('entire_region')
        if checkFullRegionElement == 'True':
            checkFullRegion = True
        else:
            checkFullRegion = False
        
        if checkFullRegion:
            print 'Identifying all geographies in the region'
            return self.retrieve_geoIds_for_all_counties()

	checkIndGeoElement = geogListElement.get('individual_geographies')
	if checkIndGeoElement == 'True':
	    checkIndGeo = True
	else:
	    checkIndGeo = False

	if checkIndGeo:
            print 'Identifying individual geographies'
            return self.parse_individual_geographies(geogListElement)
	else:
            print 'Identifying all geographies for specified counties'
	    return self.parse_county_geographies(geogListElement)

    def parse_county_geographies(self, geogListElement):
	countyIterator = geogListElement.getiterator('CountyId')
	
	countyGeoList = []
	for countyElement in countyIterator:
	    stateId = int(countyElement.get('state'))
	    countyId = int(countyElement.get('county'))
            synthesizer = countyElement.get('synthesize_county')
            if synthesizer == 'True':
                countyGeo = Geography(stateId, countyId, tract=None, bg=None)
                countyGeoList.append(countyGeo)
            else:
                continue
	return self.retrieve_geoIds_for_counties(countyGeoList) 


    def retrieve_geoIds_for_all_counties(self):
        db = MySQLdb.connect(user = '%s' %self.project.db.username,
                             passwd = '%s' %self.project.db.password,
                             db = self.project.name)
        dbc = db.cursor()     
        geoObjList = []
        try:
            dbc.execute("""select state, county, taz from geocorr""")
            results = asarray(dbc.fetchall())
            for row in results:
                geoObj = Geography(row[0], row[1], tract=1, bg = row[2])
                #print '\t', geoObj
                geoObjList.append(geoObj)
        except Exception, e:
            print ("\tError occurred when identifying geoids for entire region: %s" %e)

	dbc.close()
	db.close()
        return geoObjList

    def retrieve_geoIds_for_counties(self, countyGeoList):
        db = MySQLdb.connect(user = '%s' %self.project.db.username,
                             passwd = '%s' %self.project.db.password,
                             db = self.project.name)
        dbc = db.cursor()
	geoObjList = []
	for countyGeo in countyGeoList:
	    try:
                dbc.execute("""select state, county, taz from geocorr where state = %s and county = %s"""
                                   %(countyGeo.state, countyGeo.county))
		results = asarray(dbc.fetchall())
		for row in results:
		    geoObj = Geography(row[0], row[1], tract=1, bg = row[2])
		    #print '\t', geoObj
		    geoObjList.append(geoObj)
            except Exception, e:
	       print ("\tError occurred when identifying geoids in county: %s" %e)
	dbc.close()
	db.close()
	return geoObjList	    

    def parse_individual_geographies(self, geogListElement):
        geogIterator = geogListElement.getiterator('GeoId')
        geogObjList = []
        for geogElement in geogIterator:
            geogObj = self.return_geog_obj(geogElement)
            geogObjList.append(geogObj)
            print '\t%s' %(geogObj)
        return geogObjList


    def return_geog_obj(self, geogElement):
        state = int(geogElement.get('state'))
        county = int(geogElement.get('county'))
        taz = int(geogElement.get('taz'))

        geoObj = Geography(state, county, tract=1, bg=taz)
        return geoObj
 
    def return_location_filename(self, fullfileloc):
	loc,fileNameIncExt = os.path.split(fullfileloc)

	fileName, fileType = re.split("[.]", fileNameIncExt)
	return loc, fileName
	


    def parse_multiway_tables(self, outputElement):
	multiwayelementIter = outputElement.getiterator('MultiwayTable')
	
	multiwayTableList = []
	for multiwayElement in multiwayelementIter:
	    fullLocation = multiwayElement.get('location')
	    #name = multiwayElement.get('name')
	    location, name = self.return_location_filename(fullLocation)
	
	    tableName = multiwayElement.get('table_name')

	    nameLocObj = TableNameLoc(name, location)
	 
	    varsIterator = multiwayElement.getiterator('Variable')

	    varsList = []
	    for varsElement in varsIterator:
		name = varsElement.get('name')
	        varsList.append(name)

	    multiWayTabObj = MultiwayTable(nameLocObj, tableName, varsList)
	
	    print multiWayTabObj
	    multiwayTableList.append(multiWayTabObj)

	return multiwayTableList

    def parse_summary_table(self, outputElement):
	summaryTableElement = outputElement.find("SummaryTable")

	if summaryTableElement is not None:
	    export = True
	    #name = summaryTableElement.get('name')
	    fullLocation = summaryTableElement.get('location')
	    location, name = self.return_location_filename(fullLocation)	

	    nameLocObj = TableNameLoc(name, location)
	else:
	    export = False	
	    nameLocObj = TableNameLoc('Summary')
	return export, nameLocObj

    def parse_synthetic_population_tables(self, outputElement):
	synPopTableElement = outputElement.find("SyntheticPopulationTables")

	if synPopTableElement is not None:
	    export = True
	    #pers_name = synPopTableElement.get('person_name')
	    #housing_name = synPopTableElement.get('housing_name')
	    persFullLocation = synPopTableElement.get('person_location')
	    housingFullLocation = synPopTableElement.get('housing_location')
	
	    pers_loc, pers_name = self.return_location_filename(persFullLocation)
	    housing_loc, housing_name = self.return_location_filename(housingFullLocation)

	    persNameLocObj = TableNameLoc(pers_name, pers_loc)
	    housingNameLocObj = TableNameLoc(housing_name, housing_loc)
	else:
	    export = False
	    persNameLocObj = TableNameLoc('person_synthetic_data', location)
	    housingNameLocObj = TableNameLoc('housing_synthetic_data', location)
	return export, persNameLocObj, housingNameLocObj

if __name__ == "__main__":
    configObject = ConfigParser(fileLoc = '/home/kkonduri/simtravel/populationsynthesis/configuration/config.xml')
    configObject.parse()
