import sys

from configuration.config_parser import ConfigParser
from popgen_manager import PopgenManager

def run():
    """
    Runs the OpenAMOS program to simulate the activity-travel choices as 
    indicated by the models and their specifications in the config file.

    Please refer to OpenAMOS documentation on www.simtravel.wikispaces.asu.edu
    for guidance on setting up the configuration file.
    """
    args = sys.argv[1:]

    print args

    if len(args) < 1 or len(args) > 2:
        raise ArgumentsError, """The module accepts """\
            """only one argument which is the location of the configuration """\
            """file and second argument is an indicator for running in """\
            """ serial or parallel and is optional - 0 indicates run in serial """\
            """ otherwise it is always checks for multiple cores and runs in parallel """\
            """ when multiple cores are available."""\
            """e.g. /home/config.xml (linux machine single core) """\
            """or c:/testproject/config.xml (windows machine single core)"""\
            """e.g. /home/config.xml 1(linux machine run in parallel) """\
            """or c:/testproject/config.xml 1(windows machine run in parallel)"""\

    if len(args) == 2:
	pFlag = args[1]
    else:
    	pFlag = 1
    
    popgenManagerObject = PopgenManager(fileLoc = args[0], parallelFlag=pFlag)
    popgenManagerObject.run_scenarios()



if __name__ == "__main__":
    sys.exit(run())
