#include "interface_to_popgen.h"
 
int main(void)
{
  int intervals;
  char temp;
 
  /* All these variables are defined to build/define the array of arrival information
     that needs to be passed to python as an argument*/
 
   /* Variables for storing the reference to method*/
  PyObject *runMethod, *recs_reached_array;
  int popgenFlag;
  char fileLoc[] = "../configuration/config.xml";

 
  initialize_python_interpreter();
 
  /* Access the method for retrieving records*/
  runMethod = return_run_method(fileLoc);
 
  /*retrieving records for all the 1440 intervals*/
	
  popgenFlag = run_scenarios(runMethod);

  printf("Press any key to continue");
  finalize_python_interpreter();
  return 0;
 
}
