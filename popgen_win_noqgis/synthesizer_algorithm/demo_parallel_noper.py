# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

# Running IPF on Person and Household data

import synthesizer_algorithm.heuristic_algorithm_noper
import synthesizer_algorithm.psuedo_sparse_matrix
import synthesizer_algorithm.drawing_households
import synthesizer_algorithm.adjusting_sample_joint_distribution
import synthesizer_algorithm.ipf
from gui.file_menu.newproject import Geography
import scipy
import scipy.stats
import numpy
import MySQLdb
import time
import sys
import pp
import pickle
import os

def configure_and_run(fileLoc, geo, varCorrDict):


    f = open('indexMatrix_99999.pkl', 'rb')
    index_matrix = cPickle.load(f)
    f.close()

    f = open(fileLoc, 'rb')
    project = pickle.load(f)
    f.close()


    state, county, pumano, tract, bg = geo.state, geo.county, geo.puma5, geo.tract, geo.bg
    print '------------------------------------------------------------------'
    print 'Geography: PUMA ID- %s, Tract ID- %0.2f, BG ID- %s' \
                                                                         %(pumano, float(tract)/100, bg)
    print '------------------------------------------------------------------'

    db = MySQLdb.connect(host = '%s' %project.db.hostname, user = '%s' %project.db.username,
                         passwd = '%s' %project.db.password, db = '%s%s%s' 
                         %(project.name, 'scenario', project.scenario))

    dbc = db.cursor()

    tii = time.clock()
    ti = time.clock()

# Identifying the number of housing units in the disaggregate sample
# Make Sure that the file is sorted by hhid
    dbc.execute('select hhid, serialno from gq_sample')
    gq_sample = numpy.asarray(dbc.fetchall(), int)
    gq_units = dbc.rowcount

    dbc.execute('select hhid, serialno from hhld_sample')
    hhld_sample = numpy.asarray(dbc.fetchall(), int)
    hhld_units = dbc.rowcount

    dbc.execute('select hhid, serialno, pnum, personuniqueid from person_sample')
    person_sample = numpy.asarray(dbc.fetchall(), int)

    housing_sample = numpy.vstack((hhld_sample, gq_sample))
    housing_units = gq_units + hhld_units

# Identifying the control variables for the households, gq's
    hhld_control_variables = project.hhldVars
    gq_control_variables = project.gqVars


# Identifying the number of categories within each control variable for the households, gq's
    hhld_dimensions = project.hhldDims
    gq_dimensions = project.gqDims

# Checking marginal totals
    hhld_marginals = synthesizer_algorithm.adjusting_sample_joint_distribution.prepare_control_marginals (db, 'hhld', hhld_control_variables,
                                                                                                          varCorrDict,
                                                                                                          project.adjControlsDicts.hhld,
                                                                                    state, county, tract, bg)
    gq_marginals = synthesizer_algorithm.adjusting_sample_joint_distribution.prepare_control_marginals (db, 'gq', gq_control_variables,
                                                                                                        varCorrDict,
                                                                                                        project.adjControlsDicts.gq,
                                                                                  state, county, tract, bg)

    print 'Step 1A: Checking if the marginals totals are non-zero and if they are consistent across variables...'
    print '\tChecking household variables'
    synthesizer_algorithm.adjusting_sample_joint_distribution.check_marginals(hhld_marginals, hhld_control_variables)
    print '\tChecking gq variables\n'
    synthesizer_algorithm.adjusting_sample_joint_distribution.check_marginals(gq_marginals, gq_control_variables)
    
    print 'Step 1B: Checking if the geography has any housing units to synthesize...\n'
    synthesizer_algorithm.adjusting_sample_joint_distribution.check_for_zero_housing_totals(hhld_marginals, gq_marginals)

# Reading the parameters
    parameters = project.parameters

#______________________________________________________________________
# Running IPF for Households
    print 'Step 2A: Running IPF procedure for Households... '
    hhld_objective_frequency, hhld_estimated_constraint = synthesizer_algorithm.ipf.ipf_config_run(db, 'hhld', hhld_control_variables, varCorrDict, 
                                                                             project.adjControlsDicts.hhld,
                                                                             hhld_dimensions, 
                                                                             state, county, pumano, tract, bg, 
                                                                             parameters)
    print 'IPF procedure for Households completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for GQ
    print 'Step 2B: Running IPF procedure for Gqs... '
    gq_objective_frequency, gq_estimated_constraint = synthesizer_algorithm.ipf.ipf_config_run(db, 'gq', gq_control_variables, varCorrDict, 
                                                                         project.adjControlsDicts.gq,
                                                                         gq_dimensions, 
                                                                         state, county, pumano, tract, bg, 
                                                                         parameters)
    print 'IPF procedure for GQ was completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

#______________________________________________________________________
# Creating the weights array
    print 'Step 3: Running IPU procedure for obtaining weights that satisfy Household constraints... '
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(99999))
    result = numpy.asarray(dbc.fetchall())[:,0]
    weights = numpy.ones((1,housing_units), dtype = float)[0] * -99
    weights[result]=1

    print 'Number of housing units - %s' %housing_units
#______________________________________________________________________
# Creating the control array
    total_constraint = numpy.hstack((hhld_estimated_constraint[:,0], gq_estimated_constraint[:,0]))

#______________________________________________________________________
# Creating the sparse array
    dbc.execute('select * from sparse_matrix1_%s' %(99999))
    sp_matrix = numpy.asarray(dbc.fetchall())


#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    iteration, weights, conv_crit_array, wts_array = synthesizer_algorithm.heuristic_algorithm_noper.heuristic_adjustment(db, 0, index_matrix, weights, total_constraint, sp_matrix, parameters)

    print 'IPU procedure was completed in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()
#_________________________________________________________________
    print 'Step 4: Creating the synthetic households and individuals...'
# creating whole marginal values
    hhld_order_dummy = synthesizer_algorithm.adjusting_sample_joint_distribution.create_aggregation_string(hhld_control_variables)
    hhld_frequencies = synthesizer_algorithm.drawing_households.create_whole_frequencies(db, 'hhld', hhld_order_dummy, pumano, tract, bg, parameters)

    gq_order_dummy = synthesizer_algorithm.adjusting_sample_joint_distribution.create_aggregation_string(gq_control_variables)
    gq_frequencies = synthesizer_algorithm.drawing_households.create_whole_frequencies(db, 'gq', gq_order_dummy, pumano, tract, bg, parameters)

    frequencies = numpy.hstack((hhld_frequencies[:,0], gq_frequencies[:,0]))
    housing_objective_frequency = numpy.hstack((hhld_objective_frequency[:,0], gq_objective_frequency[:,0]))

#______________________________________________________________________
# Sampling Households and choosing the draw with the best match with with the objective distribution

    ti = time.time()

    f = open('pIndexMatrix.pkl', 'rb')
    p_index_matrix = cPickle.load(f)

    f.close()

    print 'pIndexMatrix in - %.4f' %(time.time()-ti)


    hhidRowDict = synthesizer_algorithm.drawing_households.hhid_row_dictionary(housing_sample) # row in the master matrix - hhid
    rowHhidDict = synthesizer_algorithm.drawing_households.row_hhid_dictionary(p_index_matrix) # hhid - row in the person index matrix


    p_value = 0
    max_p = 0
    min_chi = 1e10
    draw_count = 0
    while(p_value < parameters.synPopPTol and draw_count < parameters.synPopDraws):
        draw_count = draw_count + 1
        synthetic_housing_units = synthesizer_algorithm.drawing_households.drawing_housing_units(db, frequencies, weights, index_matrix, sp_matrix, 0)

# Creating synthetic hhld, and person attribute tables

        synthetic_housing_attributes, synthetic_person_attributes = synthesizer_algorithm.drawing_households.synthetic_population_properties(db, geo, synthetic_housing_units, p_index_matrix,
                                                                                                                       housing_sample, person_sample, hhidRowDict,
                                                                                                                       rowHhidDict)



        synth_housing_stat, count_housing, housing_estimated_frequency = synthesizer_algorithm.drawing_households.checking_against_joint_distribution(housing_objective_frequency,
                                                                                                                                synthetic_housing_attributes, hhld_dimensions.prod()+gq_dimensions.prod(),
                                                                                                                                pumano, tract, bg)
        stat = synth_housing_stat
        dof = count_housing - 1

        p_value = scipy.stats.stats.chisqprob(stat, dof)
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

    else:
        print 'Population with desirable p-value of %.4f was obtained in %d iterations' %(max_p, draw_count)

    #drawing_households.storing_synthetic_attributes('housing', max_p_housing_attributes, county, tract, bg, project.location, project.name)
    #drawing_households.storing_synthetic_attributes('person', max_p_person_attributes, county, tract, bg, project.location, project.name)

    if max_p_housing_attributes.shape[0] < 2500:
        synthesizer_algorithm.drawing_households.storing_synthetic_attributes1(db, 'housing', max_p_housing_attributes, county, tract, bg)
        synthesizer_algorithm.drawing_households.storing_synthetic_attributes1(db, 'person', max_p_person_attributes, county, tract, bg)
    else:
        synthesizer_algorithm.drawing_households.storing_synthetic_attributes2(db, 'housing', max_p_housing_attributes, county, tract, bg)
        synthesizer_algorithm.drawing_households.storing_synthetic_attributes2(db, 'person', max_p_person_attributes, county, tract, bg)
        

    values = (int(state), int(county), int(tract), int(bg), min_chi, max_p, draw_count, iteration, conv_crit_array[-1])
    synthesizer_algorithm.drawing_households.store_performance_statistics(db, geo, values)

    print 'Number of Synthetic Household/Group quarters - %d' %(sum(max_p_housing_attributes[:,-2]))
    for i in range(len(hhld_control_variables)):
        print '%s variable\'s marginal distribution sum is %d' %(hhld_control_variables[i], sum(hhld_marginals[i]))

    for i in range(len(gq_control_variables)):
        print '%s variable\'s marginal distribution sum is %d' %(gq_control_variables[i], sum(gq_marginals[i]))


    db.commit()
    dbc.close()
    db.close()

    print 'Blockgroup synthesized in %.4f s' %(time.clock()-tii)

def run_parallel(job_server, project, geoIds, varCorrDict):

    fileLoc = "%s/%s/%s.pop" %(project.location, project.name, project.filename)

    start = time.time()
    #print 'Number of geographies is %s'%(len(geoIds))
    modules = ('synthesizer_algorithm.heuristic_algorithm_noper',
               'synthesizer_algorithm.drawing_households',
               'synthesizer_algorithm.adjusting_sample_joint_distribution',
               'synthesizer_algorithm.ipf',
               'cPickle',
               'scipy',
               'numpy',
               'pylab',
               'MySQLdb',
               'time',
               'scipy.stats')

    #print 'Using %d cores on the processor' %(job_server.get_ncpus())

    geoIds = [Geography(geo[0], geo[1], geo[3], geo[4], geo[2]) for geo in geoIds]
    jobs = [(geo, job_server.submit(configure_and_run, (fileLoc,
                                                        geo,
                                                        varCorrDict), (), modules)) for geo in geoIds]
    for geo, job in jobs:
        job()
    #job_server.print_stats()

    #print ' Total time for %d geographies - %.2f, Timing per geography - %.2f' %(len(geoIds), time.time()-start, (time.time()-start)/len(geoIds))


