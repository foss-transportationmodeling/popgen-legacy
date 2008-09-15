# Running IPF on Person and Household data

import time
import MySQLdb
import operator
import os
from math import exp
from numpy import asarray as arr
from numpy import ones, zeros
from numpy import histogram
from scipy import sparse
from scipy import poly1d
import adjusting_pums_joint_distribution as adjusting_pums_joint_distribution


def populate_master_matrix(db, pumano, sample_size, hhld_dimensions, person_dimensions):

# In the first part we create the matrix
    hhld_types = arr(hhld_dimensions).prod()
    person_types = arr(person_dimensions).prod()

   
# We add 2 more columns to accomodate puma id, and hhld pums id. Also note that the matrix indices start from 0
# Structure of sample_matrix - puma id (0 th column), hhld pums id, hhld types, person types, wts from the entropy procedure
    total_cols = 2 + hhld_types + person_types 
   
    matrix = sparse.lil_matrix((sample_size, total_cols))
    
# In this part we populate the matrix
    dbc = db.cursor()
    for control_type in ['hhld', 'person']:
        if control_type == 'hhld':
            start = 1
        else:
            start = 1 + arr(hhld_dimensions).prod()
        if pumano == 0:
            dbc.execute('Select * from %s_pums' %(control_type))
        else:
            dbc.execute('Select * from %s_pums where pumano = %s' %(control_type, pumano))
        result = arr(dbc.fetchall())
        if control_type == 'hhld':
            rows = 0
            for i in result[:,2]:
                matrix[i - 1,:2] = result[rows,:2]
                rows = rows + 1
	for i in range(dbc.rowcount):
	    matrix[result[i, 2]-1, start+result[i, -1]] = matrix[result[i, 2]-1, start+result[i, -1]] + 1
    dbc.close()
    return matrix


def psuedo_sparse_matrix(db, matrix, pumano):
    sparse_matrix = []
    dummy = []
    rows = 0
    cols = 2
    temp_file = open('dummy.txt', 'w')
    
    for i in matrix.rows:
        if i:
            for j in i[2:]:
                dummy.append(matrix[rows, 1])
                dummy.append(rows)
                dummy.append(j)
                dummy.append(matrix.data[rows][cols])
                sparse_matrix.append(dummy)
                dummy = []
                temp_file.write(str(matrix[rows, 1]) + '\t' + str(rows) + '\t' + str(j) + '\t' + str(matrix.data[rows][cols]))
                temp_file.write('\n')
                cols = cols + 1
        cols = 2
        rows = rows + 1
    temp_file.close()

    path =  os.getcwd()+'\dummy.txt'
    path = os.path.normcase(path)
    path = path.replace('\\', '/')
    
    dbc = db.cursor()
    try:
        dbc.execute('create table sparse_matrix_%s(hhldpumsid bigint, rowno mediumint, colno mediumint, freq mediumint);'%(pumano))
        dbc.execute("load data local infile '%s' into table sparse_matrix_%s" %(path, pumano))
    except:
        dbc.execute('drop table sparse_matrix_%s'%(pumano))
        dbc.execute('create table sparse_matrix_%s(hhldpumsid bigint, rowno mediumint, colno mediumint, freq mediumint);'%(pumano))
        dbc.execute("load data local infile '%s' into table sparse_matrix_%s" %(path, pumano))
    dbc.close()
    return arr(sparse_matrix)

def generate_index_matrix(db, pumano):
    dbc = db.cursor()
    try:
        dbc.execute("drop table sparse_matrix1_%s"%(pumano))
    except:
        pass
    dbc.execute("create table sparse_matrix1_%s select * from sparse_matrix_%s order by colno, rowno"%(pumano, pumano))
    dbc.execute("alter table sparse_matrix1_%s add column id int primary key auto_increment not null first"%(pumano))
    try:
        dbc.execute("create table index_matrix_%s select colno, min(id), max(id) from sparse_matrix1_%s group by colno"%(pumano, pumano))
    except:
	dbc.execute("drop table index_matrix_%s"%(pumano))
        dbc.execute("create table index_matrix_%s select colno, min(id), max(id) from sparse_matrix1_%s group by colno"%(pumano, pumano))    
    dbc.execute("select * from index_matrix_%s"%(pumano))
    result = dbc.fetchall()
    index_matrix = arr(result)
    dbc.close()       
    return index_matrix



if __name__ == '__main__':

    sample_size = 156601
    pumano = 0

    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'ncpopsyn')
    
    hhld_dimensions = arr([5,7,8])
    person_dimensions = arr([2, 10, 7])

    hhld_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'hhld')
    person_control_variables = adjusting_pums_joint_distribution.choose_control_variables(db, 'person')

    update_string = adjusting_pums_joint_distribution.create_update_string(db, hhld_control_variables, hhld_dimensions)
    adjusting_pums_joint_distribution.add_unique_id(db, 'hhld', update_string)

    update_string = adjusting_pums_joint_distribution.create_update_string(db, person_control_variables, person_dimensions)
    adjusting_pums_joint_distribution.add_unique_id(db, 'person', update_string)

    ti = time.clock()
    print 'start - %s'%ti
    populated_matrix = populate_master_matrix(db, pumano, sample_size, hhld_dimensions, person_dimensions)
    print 'End Populated matrix - %s'%(time.clock()-ti)


    ti = time.clock()
    ps_sp_matrix = psuedo_sparse_matrix(db, populated_matrix, pumano)
    print 'Psuedo Sparse Matrix- %s'%(time.clock()-ti)
    

    index = generate_index_matrix(db, 0)
    
