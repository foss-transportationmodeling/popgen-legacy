# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2010, Arizona State University
# See PopGen/License

import copy
from lxml import etree
from numpy import array
from collections import defaultdict
from newproject import *


class ConfigParser(object):
    def __init__(self, configObject):
        if not isinstance(configObject, etree._ElementTree):
            print ConfigurationError, """The configuration object input is not a valid """\
                """etree.Element object. Trying to load the object from the configuration"""\
                """ file."""

        self.configObject = configObject


    def parse(self):

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

        scenarioList = []
        scenarioIterator = self.configObject.getiterator('Scenario')

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
        scenarioProjObj.desription = description

        #Checking to see if data needs to be prepared
        prepareData = scenarioElement.get('prepare_data')
        if prepareData == 'True':
            scenarioProjObj.prepareData = True
        if prepareData == 'False':
            scenarioProjObj.prepareData = False


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
	    else:
		scenarioProjObj.selVariableDicts.hhldMargsModify = False
            hhldSizeVar, aveHhldSize, refPersVar = self.parse_modified_marginals(margAdjElement)
            scenarioProjObj.selVariableDicts.hhldSizeVarName = hhldSizeVar
            scenarioProjObj.selVariableDicts.aveHhldSizeLastCat = aveHhldSize
            scenarioProjObj.selVariableDicts.refPersName = refPersVar

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
	    adjMargs = self.parse_adjust_marginals(adjustMargElement)
            scenarioProjObj.adjControlsDicts.hhld = adjMargs
            scenarioProjObj.adjControlsDicts.gq = adjMargs
            scenarioProjObj.adjControlsDicts.person = adjMargs

        geogListElement = scenarioElement.find('SynthesizeGeographies')
        geogObjList = self.parse_geographies(geogListElement)
        scenarioProjObj.synthesizeGeoIds = geogObjList

    def parse_scenario_attribs(self, scenarioElement):
        scenario = scenarioElement.get('value')
        description = scenarioElement.get('description')

        return scenario, description


    def parse_control_variables(self, controlVarsElement, controlType):
        controlTypeElement = controlVarsElement.find(controlType)

        variables = []
        variableDims = []
        

        varsIterator = controlTypeElement.getiterator('Variable')
        for varElement in varsIterator:
            name = varElement.get('name')
            numCats = int(varElement.get('num_categories'))
            variables.append(name)
            variableDims.append(numCats)

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
	tract = geoIdElement.get('tract')
	bg = geoIdElement.get('bg')
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
        geogIterator = geogListElement.getiterator('GeoId')

        geogObjList = []
        print 'LIST OF GEOGRAPHIES TO BE SYNTHESIZED'
        for geogElement in geogIterator:
            geogObj = self.return_geog_obj(geogElement)
            geogObjList.append(geogObj)
            print '\t%s' %(geogObj)
        print
        return geogObjList

    def return_geog_obj(self, geogElement):
        state = geogElement.get('state')
        county = geogElement.get('county')
        tract = geogElement.get('tract')
        bg = geogElement.get('bg')
        pumano = geogElement.get('pumano')

        geoObj = Geography(state, county, tract, bg, pumano)
        return geoObj


if __name__ == "__main__":
    configObject = ConfigParser(fileLoc = '/home/kkonduri/simtravel/populationsynthesis/configuration/config.xml')
    configObject.parse()
