#ifndef PYDHT11
#include <stdlib.h>
#include <Python.h>
#include "DHT11.h"
static PyObject* Call_DHT11(PyObject *self, PyObject *args);
static PyObject* Init_WiringPi(PyObject *self, PyObject *args);

// registration table
static struct PyMethodDef methods[] =
{
    {"read_DHT11", Call_DHT11, METH_NOARGS, "read DHT11 sensors data"},
    {"Init_WiringPi", Init_WiringPi, METH_NOARGS, "initialization wiring pi functions"},
    { NULL, NULL}
};
// initialization

PyMODINIT_FUNC initDHT11(void);
#endif
