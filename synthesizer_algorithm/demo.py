# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

# Running IPF on Person and Household data

import os

import heuristic_algorithm
import psuedo_sparse_matrix
import drawing_households
import adjusting_sample_joint_distribution
import ipf
import scipy
import scipy.stats
import numpy
import MySQLdb
import time
import cPickle

def configure_and_run(project, geo, varCorrDict):

    f = open('%s%s%s%sindexMatrix_99999.pkl'%(project.location, os.path.sep,
					      project.name, os.path.sep), 'rb')
    index_matrix = cPickle.load(f)
    f.close()


    state, county, pumano, tract, bg = geo.state, geo.county, geo.puma5, geo.tract, geo.bg
    print '------------------------------------------------------------------'
    print 'Geography: County - %s, PUMA ID- %s, Tract ID- %0.2f, BG ID- %s' \
                                                                         %(county, pumano, float(tract)/100, bg)
    print '------------------------------------------------------------------'

    db = MySQLdb.connect(host = '%s' %project.db.hostname, user = '%s' %project.db.username,
                         passwd = '%s' %project.db.password, db = '%s%s%s' 
                         %(project.name, 'scenario', project.scenario))
    dbc = db.cursor()

    tii = time.clock()
    ti = time.clock()

# Identifying the number of housing units in the disaggregate sample
# Make Sure that the file is sorted by hhid
    dbc.execute('select hhid, serialno from gq_sample order by hhid')
    gq_sample = numpy.asarray(dbc.fetchall(), numpy.int64)
    gq_units = dbc.rowcount

    dbc.execute('select hhid, serialno from hhld_sample order by hhid')
    hhld_sample = numpy.asarray(dbc.fetchall(), numpy.int64)
    hhld_units = dbc.rowcount

    dbc.execute('select hhid, serialno, pnum, personuniqueid from person_sample order by hhid, pnum')
    person_sample = numpy.asarray(dbc.fetchall(), numpy.int64)

    housing_sample = numpy.vstack((hhld_sample, gq_sample))
    housing_units = gq_units + hhld_units

# Identifying the control variables for the households, gq's, and persons
    hhld_control_variables = project.hhldVars
    gq_control_variables = project.gqVars
    person_control_variables = project.personVars

# Identifying the number of categories within each control variable for the households, gq's, and persons
    hhld_dimensions = project.hhldDims
    gq_dimensions = project.gqDims
    person_dimensions = project.personDims

# Checking marginal totals
    hhld_marginals = adjusting_sample_joint_distribution.prepare_control_marginals (db, 'hhld', hhld_control_variables, varCorrDict, project.adjControlsDicts.hhld,
                                                                                    state, county, tract, bg, project.selVariableDicts.hhldMargsModify)
    gq_marginals = adjusting_sample_joint_distribution.prepare_control_marginals (db, 'gq', gq_control_variables, varCorrDict, project.adjControlsDicts.gq,
                                                                                  state, county, tract, bg)
    person_marginals = adjusting_sample_joint_distribution.prepare_control_marginals (db, 'person', person_control_variables, varCorrDict, project.adjControlsDicts.person,
                                                                                      state, county, tract, bg)
    print 'Step 1A: Checking if the marginals totals are non-zero and if they are consistent across variables...'
    print '\tChecking household variables'
    adjusting_sample_joint_distribution.check_marginals(hhld_marginals, hhld_control_variables)
    print '\tChecking gq variables'
    adjusting_sample_joint_distribution.check_marginals(gq_marginals, gq_control_variables)
    print '\tChecking person variables\n'
    adjusting_sample_joint_distribution.check_marginals(person_marginals, person_control_variables)
    
    print 'Step 1B: Checking if the geography has any housing units to synthesize...\n'
    adjusting_sample_joint_distribution.check_for_zero_housing_totals(hhld_marginals, gq_marginals)

    print 'Step 1C: Checking if the geography has any persons to synthesize...\n'
    adjusting_sample_joint_distribution.check_for_zero_person_totals(person_marginals)


# Reading the parameters
    parameters = project.parameters

#______________________________________________________________________
# Running IPF for Households
    print 'Step 2A: Running IPF procedure for Households... '
    hhld_objective_frequency, hhld_estimated_constraint = ipf.ipf_config_run(db, 'hhld', hhld_control_variables, varCorrDict, 
                                                                             project.adjControlsDicts.hhld,
                                                                             hhld_dimensions, 
                                                                             state, county, pumano, tract, bg, 
                                                                             parameters, project.selVariableDicts.hhldMargsModify)
    print 'IPF procedure for Households completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for GQ
    print 'Step 2B: Running IPF procedure for Gqs... '
    gq_objective_frequency, gq_estimated_constraint = ipf.ipf_config_run(db, 'gq', gq_control_variables, varCorrDict, 
                                                                         project.adjControlsDicts.gq,
                                                                         gq_dimensions, 
                                                                         state, county, pumano, tract, bg, 
                                                                         parameters)
    print 'IPF procedure for GQ was completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for Persons
    print 'Step 2C: Running IPF procedure for Persons... '
    person_objective_frequency, person_estimated_constraint = ipf.ipf_config_run(db, 'person', person_control_variables, 
                                                                                 varCorrDict, 
                                                                                 project.adjControlsDicts.person,
                                                                                 person_dimensions, 
                                                                                 state, county, 
                                                                                 pumano, tract, bg, parameters)
    print 'IPF procedure for Persons completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()
#______________________________________________________________________
# Creating the weights array
    print 'Step 3: Running IPU procedure for obtaining weights that satisfy Household and Person type constraints... '
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(99999))
    result = numpy.asarray(dbc.fetchall())[:,0]
    weightsDef = numpy.ones((1,housing_units), dtype = float)[0] * -99
    weightsDef[result]=1

    print 'Number of housing units - %s' %housing_units
#______________________________________________________________________
# Creating the control array
    total_constraint = numpy.hstack((hhld_estimated_constraint[:,0], gq_estimated_constraint[:,0], person_estimated_constraint[:,0]))

#______________________________________________________________________
# Creating the sparse array
    dbc.execute('select * from sparse_matrix1_%s' %(99999))
    sp_matrix = numpy.asarray(dbc.fetchall())


#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    weightsDef = numpy.ones((1,housing_units), dtype = float)[0] * -99
    weightsDef[result]=1
    if project.parameters.ipuProcedure == "ProportionalUpdating":
	print 'Employing the proportional updating procedure for reallocating sample weights', project.parameters.ipuProcedure
    	iteration, weights, conv_crit_array, wts_array = heuristic_algorithm.heuristic_adjustment(db, 0, index_matrix, weightsDef, total_constraint, sp_matrix, parameters)
    elif project.parameters.ipuProcedure == 'EntropyUpdating':
	print 'Employing the entropy-based updating procedure for reallocating sample weights', project.parameters.ipuProcedure
    	iteration, weights, conv_crit_array, wts_array = heuristic_algorithm.ipu_entropy(db, 0, index_matrix, weightsDef, total_constraint, sp_matrix, parameters)

    """
    diff = weights - weights1

    f = open('weightsComp.csv', 'w')
		
    for i in range(housing_units):
	f.write('%s,%s,%s\n' %(weights[i], weights1[i], diff[i]))
    f.close()
    """
    print 'IPU procedure was completed in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()
#_________________________________________________________________
    print 'Step 4: Creating the synthetic households and individuals...'
# creating whole marginal values
    hhld_order_dummy = adjusting_sample_joint_distribution.create_aggregation_string(hhld_control_variables)
    hhld_frequencies = drawing_households.create_whole_frequencies(db, 'hhld', hhld_order_dummy, pumano, tract, bg, parameters)

    gq_order_dummy = adjusting_sample_joint_distribution.create_aggregation_string(gq_control_variables)
    gq_frequencies = drawing_households.create_whole_frequencies(db, 'gq', gq_order_dummy, pumano, tract, bg, parameters)

    frequencies = numpy.hstack((hhld_frequencies[:,0], gq_frequencies[:,0]))

#______________________________________________________________________
# Sampling Households and choosing the draw with the best match with with the objective distribution

    ti = time.time()

    f = open('%s%s%s%spIndexMatrix.pkl'%(project.location, os.path.sep,
					 project.name, os.path.sep), 'rb')
    p_index_matrix = cPickle.load(f)

    f.close()

    hhidRowDict = drawing_households.hhid_row_dictionary(housing_sample) # row in the master matrix - hhid
    rowHhidDict = drawing_households.row_hhid_dictionary(p_index_matrix) # hhid - row in the person index matrix


    p_value = 0
    max_p = 0
    min_chi = 1e10
    draw_count = 0
    while(p_value < parameters.synPopPTol and draw_count < parameters.synPopDraws):
        draw_count = draw_count + 1
        synthetic_housing_units = drawing_households.drawing_housing_units(db, frequencies, weights, index_matrix, sp_matrix, 0, drawingProcedure=project.parameters.drawingProcedure)


# Creating synthetic hhld, and person attribute tables

        synthetic_housing_attributes, synthetic_person_attributes = drawing_households.synthetic_population_properties(db, geo, synthetic_housing_units, p_index_matrix,
                                                                                                                       housing_sample, person_sample, hhidRowDict,
                                                                                                                       rowHhidDict)

	"""
	objective_frequency = numpy.hstack((hhld_objective_frequency[:,0], gq_objective_frequency[:,0], person_objective_frequency[:,0]))
	
	print synthetic_housing_attributes[:,-2:].shape, synthetic_person_attributes[:,-2:].shape

	print 'before', synthetic_person_attributes[:,-1]
	persAttrs = synthetic_person_attributes[:,-2:]
	persAttrs[:,-1] += hhld_dimensions.prod() + gq_dimensions.prod()
	synthetic_attributes = numpy.vstack((synthetic_housing_attributes[:,-2:], persAttrs))
	print 'after', synthetic_person_attributes[:,-1]
	print objective_frequency.shape, synthetic_housing_attributes[:,-2:].shape
	
        stat, dof, person_estimated_frequency = drawing_households.checking_against_joint_distribution(objective_frequency, synthetic_attributes,
												       hhld_dimensions.prod() + gq_dimensions.prod() + person_dimensions.prod(),
                                                                                                       pumano, tract, bg)

	"""
        synth_person_stat, count_person, person_estimated_frequency = drawing_households.checking_against_joint_distribution(person_objective_frequency,
                                                                                                                             synthetic_person_attributes, person_dimensions.prod(),
                                                                                                                             pumano, tract, bg)
        stat = synth_person_stat
        dof = count_person - 1

	if dof == 0:
	    p_value = 1
	else:
	    p_value = scipy.stats.chisqprob(stat, dof)

        if p_value > max_p or stat < min_chi:
            max_p = p_value
            max_p_housing_attributes = synthetic_housing_attributes
            max_p_person_attributes = synthetic_person_attributes
            min_chi = stat

    sp_matrix = None

    if draw_count >= parameters.synPopDraws:
        print ('Max Iterations (%d) reached for drawing households with the best draw having a p-value of %.4f'
               %(parameters.synPopDraws, max_p))
        if max_p == 0:
            max_p = p_value
            max_p_housing_attributes = synthetic_housing_attributes
            max_p_person_attributes = synthetic_person_attributes
            min_chi = stat

        print 'draw_count - %s, pvalue - %s, chi value - %s' %(draw_count, p_value, stat)
    else:
        print 'Population with desirable p-value of %.4f was obtained in %d iterations' %(max_p, draw_count)

    #drawing_households.storing_synthetic_attributes('housing', max_p_housing_attributes, county, tract, bg, project.location, project.name)
    #drawing_households.storing_synthetic_attributes('person', max_p_person_attributes, county, tract, bg, project.location, project.name)

    if max_p_housing_attributes.shape[0] < 2500:
        drawing_households.storing_synthetic_attributes1(db, 'housing', max_p_housing_attributes, county, tract, bg)
        drawing_households.storing_synthetic_attributes1(db, 'person', max_p_person_attributes, county, tract, bg)
    else:
        drawing_households.storing_synthetic_attributes2(db, 'housing', max_p_housing_attributes, county, tract, bg)
        drawing_households.storing_synthetic_attributes2(db, 'person', max_p_person_attributes, county, tract, bg)
        

    values = (int(state), int(county), int(tract), int(bg), min_chi, max_p, draw_count, iteration, conv_crit_array[-1])
    drawing_households.store_performance_statistics(db, geo, values)

    print 'Number of Synthetic Household/Group quarters - %d' %((max_p_housing_attributes[:,-2]).sum())
    for i in range(len(hhld_control_variables)):
        print '%s variable\'s marginal distribution sum is %d' %(hhld_control_variables[i], round(sum(hhld_marginals[i])))

    for i in range(len(gq_control_variables)):
        print '%s variable\'s marginal distribution sum is %d' %(gq_control_variables[i], round(sum(gq_marginals[i])))


    print 'Number of Synthetic Persons - %d' %((max_p_person_attributes[:,-2]).sum())
    for i in range(len(person_control_variables)):
        print '%s variable\'s marginal distribution sum is %d' %(person_control_variables[i], round(sum(person_marginals[i])))
    print 'Synthetic households created for the geography in %.2f\n' %(time.time()-ti)



    db.commit()
    dbc.close()
    db.close()
    print 'Blockgroup synthesized in %.4f s' %(time.clock()-tii)

if __name__ == '__main__':

    start = time.clock()
    ti = time.clock()
    db = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1234', db = 'aacog')
    dbc = db.cursor()
#______________________________________________________________________
#Reading the Index Matrix
    dbc.execute("select * from index_matrix_%s"%(0))
    result = dbc.fetchall()
    index_matrix = numpy.asarray(result)
#______________________________________________________________________
# Creating person index_matrix
    p_index_matrix = drawing_households.person_index_matrix(db)
#______________________________________________________________________
# This is the serial implementation of the code

    geography = (5601, 170401, 3)
    configure_and_run(index_matrix, p_index_matrix, geography)
    print 'Synthesis for the geography was completed in %.2f' %(time.clock()-ti)

    dbc.close()
    db.commit()
    db.close()
