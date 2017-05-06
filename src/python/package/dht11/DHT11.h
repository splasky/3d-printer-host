#ifndef DHT11
#include <stdlib.h>
#include <wiringPi.h>
#define MAXTIMINGS  255
#define DHTPIN      2

typedef struct
{
    uint8_t humidity;
    uint8_t humidityfloat;
    uint8_t temperature;
    uint8_t temperaturefloat;
    uint8_t checksum;
} DHT11Data;

void read_dht11_data(DHT11Data *data, uint8_t wiringPi_Pin);

#endif /* ifndef SYMBOL */
