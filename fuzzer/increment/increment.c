#include <Python.h>

static PyObject *MaximumIncrementReached;

static PyMethodDef IncrementMethods[] = {
    {"increment",  increment_increment, METH_VARARGS | METH_KEYWORDS,
     "Increment a list for the fuzzer."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initincrement(void){
	PyObject *m;

    m = Py_InitModule("increment", IncrementMethods);
    MaximumIncrementReached = PyErr_NewException(NULL, NULL, NULL);
    Py_INCREF(MaximumIncrementReached);
    PyModule_AddObject(m, "Incrimentation limit reached.", MaximumIncrementReached);
}

static PyObject *
increment_increment(PyObject *self, PyObject *args, PyObject *kwargs)
{
	PyListObject *values;
    int index;
    int minimum = 0;
    int maximum = 255;
    PyObject reset;
    PyObject _called_from_func = false;
    static char *kwlist[] = {"minimum", "maximum", 
                             "reset", "_called_from_func", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs,
    								 "Oi|iiOO", kwlist,
    	                             &values, &index
    	                             &minimum, &maximum,
    	                             &reset, &_called_from_func ))
        return NULL;
    if (index >= 0){
    	if (PyList_GetItem(values, index)+1 >= maximum){
    		if (PyObject_IsTrue(_called_from_func)
    			&& index == 0){
    
    		}
    	}
    }
    return Py_BuildValue("i", sts);
}