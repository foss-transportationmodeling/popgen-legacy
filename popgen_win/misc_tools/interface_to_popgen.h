#include <Python.h>


#ifdef __cplusplus
extern "C" {
#endif


void error(char *errstring)
{
  printf("Error:%s\n",errstring);
  exit(1);
}


void type(char *typestring)
{
  printf("%s\n",typestring);
}

PyObject* return_run_method(char *fileLoc)
{
  	PyObject *mod, *popgenManagerClass, *classobject, *args_class, *runMethod;

  	mod = PyImport_ImportModule("popgen_manager");

  	if (mod == NULL){
		Py_DECREF(mod);
		char msg[] = "Can't open module";
		error(msg);
    	}
	else{
     	 	type("Opened module for popgen manager...");
    	}

  	/*Creating a reference to the class which retrieves the records*/
  	popgenManagerClass = PyObject_GetAttrString(mod, "PopgenManager");
  	Py_DECREF(mod);

  	if (popgenManagerClass == NULL){
		Py_DECREF(popgenManagerClass);
		char msg[] = "Can't find reference to class for running PopGen";
		error(msg);

    	}
	else{
      		type("Found reference to class for running PopGen...");
    	}

  	/*Creating arguments for the class*/
  	args_class = Py_BuildValue("(s)", fileLoc);

	if (args_class == NULL){
      		Py_XDECREF(args_class); 
		char msg[] = "Can't build the arguments for the cl  	import_array();ass initialization";
		error(msg);
	}
	else{
      		type("Class arguments were built...");
    	}

  	/*Creating class object with the arguments*/
  	classobject = PyEval_CallObject(popgenManagerClass, args_class);

  	Py_DECREF(popgenManagerClass);
  	Py_DECREF(args_class);

  	if (classobject == NULL){
      		Py_XDECREF(classobject);//(HS) Changed
		char msg[] = "Can't initalize the class object";
		error(msg);
    	}
	else{
      		type("Class object was built...");
    	}

  	/*Creating a reference to the method within the class object for retrieving records*/
  	runMethod = PyObject_GetAttrString(classobject, "run_scenarios");
  	Py_DECREF(classobject);

  	if (runMethod == NULL){
      		Py_XDECREF(runMethod); //(HS) Changed from Py_DECREF
		char msg[] = "Can't find referennce to the method";
		error(msg);
    	}
	else{
      		type("Found reference to the method...");
    	}
  	return runMethod;
} 

int run_scenarios(PyObject *runMethod)

{
  	PyObject *args, *results;

  	/*Creating a list of arguments (time_interval) to be passed to retrieve the records*/
  	args = Py_BuildValue("()");

  	if (args == NULL)
    	{
		Py_XDECREF(args); //(HS) Changed by Hyunsoo
		char msg[] = "\n\t1. Can't build argument list to pass from C to Python";
		error(msg);
    	}else{
		char msg[] = "\n\t1. Argument list was built and passed from C to Python...";
		type(msg);
    	}


  	/*Retrieving the results and converting into c-objects*/
  	results = PyEval_CallObject(runMethod, args);

  	Py_DECREF(args);
  	if (results == NULL)
    	{
      		Py_XDECREF(results); //(HS)Changed by Hyunsoo
		char msg[] = "\n\t5. No results returned from Python";
		error(msg);
      		//error("\n\t5. No results returned from Python");
    	}else{
		char msg[] = "\n\t5. Results retrieved and returned from Python...";
		type(msg);
		//type("\n\t5. Results retrieved and returned from Python...");
	}

	return 1;
}


void initialize_python_interpreter(void)
{
	printf("PYTHON INTEPRETER INITIALIZED\n");
  	Py_Initialize();
}

void finalize_python_interpreter(void)
{
  	printf("PYTHON INTEPRETER FINALIZED\n");
  	Py_Finalize();
}


#ifdef __cplusplus
}
#endif


/* Methods:
   1. create reference to the class, the methods and return reference to the method
   2. build arguments for the method and call the method along with the arguments, 
   convert the returned object to array object; check to see if there are records to be passed
   3. if records are to be passed maybe show some logs*/
