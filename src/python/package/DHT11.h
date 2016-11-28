#ifndef DHT11
#include <stdlib.h>
#include <Python.h>
#define MAXTIMINGS  85
#define DHTPIN      7

typedef struct
{
    uint8_t humidity;
    uint8_t humidityfloat;
    uint8_t temperature;
    uint8_t temperaturefloat;
    uint8_t checksum;
} DHT11Data;

void read_dht11_data(DHT11Data *data);
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

#endif /* ifndef SYMBOL */
