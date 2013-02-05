# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import adjusting_sample_joint_distribution_nosql
import numpy

def ipf_config_run (db, synthesis_type, control_variables, varCorrDict, controlAdjDict, 
                    dimensions, state, county, pumano, tract, bg, parameters, hhldsizeMargsMod=False):

# Creating the joint distributions corrected for Zero-cell and Zero-marginal problems
# Example puma x composite_type adjustment for the synthesis type obtained as a parameter
    print '\tUsing IPF with no SQL implementation ... '
    dbc = db.cursor()

    order_dummy = adjusting_sample_joint_distribution_nosql.create_aggregation_string(control_variables)

    data, variable_names = adjusting_sample_joint_distribution_nosql.create_joint_dist(db, synthesis_type, control_variables, dimensions, pumano, tract, bg)

    data = adjusting_sample_joint_distribution_nosql.create_adjusted_frequencies_nosql(db, data, synthesis_type, control_variables, pumano, tract, bg)

    #raw_input("Check raw adjusted frequencies to correct for zero cells")

    adjusting_sample_joint_distribution_nosql.adjust_weights_nosql(db, data, variable_names, synthesis_type, control_variables, dimensions, 				varCorrDict, controlAdjDict,
			state, county, pumano, tract, bg, parameters, hhldsizeMargsMod)

    dbc.execute('select frequency from %s_%s_joint_dist where tract = %s and bg = %s order by %s'%(synthesis_type, pumano, tract, bg, order_dummy))
    estimated_constraint = numpy.asarray(dbc.fetchall())
    #print 'USING SQL PROCEDURE', estimated_constraint[:,0], estimated_constraint[:,0].sum()
    #raw_input("Check adjusted frequencies after IPF")
    objective_frequency = estimated_constraint

    dbc.close()
    db.commit()
    return objective_frequency, estimated_constraint
