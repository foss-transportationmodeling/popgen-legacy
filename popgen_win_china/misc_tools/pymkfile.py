#!/usr/local/bin/python
import distutils.sysconfig
import string, sys
configopts = {}
maketemplate = """
PYLIB=%(pythonlib)s
PYINC=-I%(pythoninc)s
LIBS=%(pylibs)s
OPTS=%(pyopt)s
PROGRAMS=%(programs)s
all: $(PROGRAMS)
"""

configopts['pythonlib'] = distutils.sysconfig.get_config_var('LIBPL') + '/' + distutils.sysconfig.get_config_var('LIBRARY')
configopts['pythoninc'] = ''
configopts['pylibs'] = ''
for dir in string.split(distutils.sysconfig.get_config_var('INCLDIRSTOMAKE')):
	configopts['pythoninc'] += '-I%s ' % (dir,)
for dir in string.split(distutils.sysconfig.get_config_var('LIBDIR')):
	configopts['pylibs'] += '-L%s ' % (dir,)

configopts['pylibs'] += distutils.sysconfig.get_config_var('MODLIBS') \
    + ' ' + \
    distutils.sysconfig.get_config_var('LIBS') \
    + ' ' + \
    distutils.sysconfig.get_config_var('SYSLIBS')	
configopts['pyopt'] = distutils.sysconfig.get_config_var('OPT')
configopts['pythoninc'] +='-I/usr/local/lib/python2.6/dist-packages/numpy/core/include/numpy'
targets = ''
for arg in sys.argv[1:]:
	targets += arg + ' '
configopts['programs'] = targets

print maketemplate % configopts

import distutils.sysconfig as ds
link_st = ds.get_config_var('LINKFORSHARED')

for arg in sys.argv[1:]:
	print "%s: %s.o\n\tg++ -fopenmp %s.o $(LIBS) $(PYLIB) -o %s %s" \
		% (arg, arg, arg, arg, link_st)
	print "%s.o: %s.cpp\n\tg++ -fopenmp %s.cpp -c $(PYINC) $(OPTS) %s" \
		% (arg, arg, arg, link_st)

print "clean:\n\trm -f $(PROGRAMS) *.o *.pyc core"

