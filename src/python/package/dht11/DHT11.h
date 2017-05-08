#ifndef __DHT11_H__
#define __DHT11_H__
#include <stdlib.h>
#include <wiringPi.h>
#include <stdint.h>
#define MAXTIMINGS  255
#define DHTPIN      2

typedef struct
{
    int8_t humidity;
    int8_t humidityfloat;
    int8_t temperature;
    int8_t temperaturefloat;
    int8_t checksum;
} DHT11Data;

void read_dht11_data(DHT11Data *data, int8_t wiringPi_Pin);

#endif /* ifndef SYMBOL */
