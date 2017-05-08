#include "PyDHT11.h"

static PyObject* Call_DHT11(PyObject *self, PyObject *args)
{
    DHT11Data data =  {0, 0, 0, 0, 0};

    read_dht11_data(&data, PIN);

    return Py_BuildValue("(iiiii)", data.humidity,
                         data.humidityfloat, data.temperature, data.temperaturefloat, data.checksum);
}

static PyObject* Init_WiringPi(PyObject *self, PyObject *args)
{

    if ( wiringPiSetup() == -1 )
        exit( 1 );
    return Py_BuildValue("i", 1);
}


// initialization

PyMODINIT_FUNC initDHT11(void)
{
    (void)Py_InitModule("DHT11", methods);
}
