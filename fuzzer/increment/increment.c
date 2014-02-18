#include <Python.h>


//Define internal generator state
typedef struct{
  PyObject_HEAD
  PyListObject values;
  PyIntObject  index;
  PyIntObject maximum;
  PyIntObject minimum;
  PyObject reset;
} generator_state;

//Define functions in the module
static PyMethodDef IncrementMethods[] = {
    {"increment",  increment_increment, METH_VARARGS | METH_KEYWORDS,
     "Increment a list for the fuzzer."},
     /* Sentinel */
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initincrement(void){
	//TODO: implement
}


PyObject*
increment_increment_iternext(PyObject *self){
    generator_state *state = (generator_state *)self;

    if (state->index >= 0){
    	if ((PyList_GetItem(state->values, state->index)+1) >= state->maximum){
	    	if (state->index == 0){
	    		//we hit the first values maximum, bail out
	    		PyErr_SetNone(PyExc_StopIteration);
	            return NULL;
	        }
	    	if (PyObject_IsTrue(state->reset)){
	    		//reset the index
	    		PyList_SetItem(state->values, state->index, state-> minimum);
	    		//move index to the left
	    		(state->index)--;
	    		PyObject *tmp = state->values;
	    		//return copy of the list
	    		return tmp;
	    	} else {
	    	    //do not reset, but move left and incriment
	    	    (state->index)--;
	    	    PyList_SetItem()
	    } else{
	    	PyList_SetItem(state->values, state->index,
	    		           PyList_GetItem(state->values,state->index)+1);
	    	PyObject *tmp = state->values;
	    	return tmp;
	    }
    }
}
PyObject*
increment_increment_iter(PyObject *self){
	Py_INCREF(self);
	return self;
}