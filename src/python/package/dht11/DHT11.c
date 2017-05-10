/*
 *  dht11.c:
 *  Simple test program to test the wiringPi functions
 *  DHT11 test
 */

#include "DHT11.h"
#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>

#define COUNTER_MAX 255
int read_dht11_data(DHT11Data* data, int8_t wiringPi_Pin)
{
    uint8_t laststate = HIGH;
    uint8_t counter = 0;
    uint8_t j = 0, i;
    float f; /* fahrenheit */
    uint8_t dht11_data[] = { 0, 0, 0, 0, 0 };

    data->checksum = 0;
    data->temperature = 0;
    data->temperaturefloat = 0;
    data->humidity = 0;
    data->humidityfloat = 0;

    pinMode(wiringPi_Pin, OUTPUT);
    digitalWrite(wiringPi_Pin, LOW);
    delay(20);
    digitalWrite(wiringPi_Pin, HIGH);
    delayMicroseconds(40);
    /* prepare to read the pin */
    pinMode(wiringPi_Pin, INPUT);

    /* detect change and read data */
    for (i = 0; i < MAXTIMINGS; i++) {
        counter = 0;
        while (digitalRead(DHTPIN) == laststate) {
            counter++;
            delayMicroseconds(1);
            if (counter == 255) {
                break;
            }
        }
        laststate = digitalRead(DHTPIN);

        if (counter == 255)
            break;

        /* ignore first 3 transitions */
        if ((i >= 4) && (i % 2 == 0)) {
            /* shove each bit into the storage bytes */
            dht11_data[j / 8] <<= 1;
            if (counter > 24)
                dht11_data[j / 8] |= 1;
            j++;
        }
    }

    data->humidity = dht11_data[0];
    data->humidityfloat = dht11_data[1];
    data->temperature = dht11_data[2];
    data->temperaturefloat = dht11_data[3];
    data->checksum = dht11_data[4];

    if ((j >= 40) && (data->checksum == ((data->humidity + data->humidityfloat
                                             + data->temperature + data->temperaturefloat)
                                            & 0xFF))) {
        f = data->temperature * 9. / 5. + 32;
#ifdef DEBUG
        printf("Humidity = %d.%d %% Temperature = %d.%d *C (%.1f *F)\n", data->humidity,
            data->humidityfloat, data->temperature, data->temperaturefloat, f);
#endif
        return 0;
    } else {
#ifdef DEBUG
        printf("Data not good, skip\n");
#endif
        return -1;
    }
}
