/*
 *  dht11.c:
 *  Simple test program to test the wiringPi functions
 *  DHT11 test
 */

#include <wiringPi.h>
#include "DHT11.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define COUNTER_MAX 255
void read_dht11_data(DHT11Data *data, uint8_t wiringPi_Pin)
{
    int dht11_dat[5] = {0, 0, 0, 0, 0};

    uint8_t laststate   = HIGH;
    uint8_t counter     = 0;
    uint8_t j       = 0, i;
    float   f; /* fahrenheit */

    dht11_dat[0] = dht11_dat[1] = dht11_dat[2] = dht11_dat[3] = dht11_dat[4] = 0;

    pinMode( wiringPi_Pin, OUTPUT );
    digitalWrite( wiringPi_Pin, LOW );
    delay( 18 );
    digitalWrite( wiringPi_Pin, HIGH );
    delayMicroseconds( 40 );
    /* prepare to read the pin */
    pinMode( wiringPi_Pin, INPUT );

    /* detect change and read data */
    for ( i = 0; i < MAXTIMINGS; i++ )
    {
        counter = 0;
        while ( digitalRead( wiringPi_Pin ) == laststate )
        {
            counter++;
            delayMicroseconds( 1 );
            if ( counter == COUNTER_MAX )
            {
                break;
            }
        }

        laststate = digitalRead( wiringPi_Pin );

        if ( counter == COUNTER_MAX )
            break;

        /* shove each bit into the storage bytes */
        dht11_dat[j / 8] <<= 1;
        if ( counter > 16 )
            dht11_dat[j / 8] |= 1;
        j++;
    }

    if ( (j >= 40) &&
            (dht11_dat[4] == ( (dht11_dat[0] + dht11_dat[1] + dht11_dat[2] + dht11_dat[3]) & 0xFF) ) )
    {
        f = dht11_dat[2] * 9. / 5. + 32;
        data->humidity = dht11_dat[0];
        data->humidityfloat = dht11_dat[1];
        data->temperature = dht11_dat[2];
        data->temperaturefloat = dht11_dat[3];
        data->checksum = dht11_dat[4];

#ifdef DEBUG
        printf( "Humidity = %d.%d %% Temperature = %d.%d *C (%.1f *F)\n",
                dht11_dat[0], dht11_dat[1], dht11_dat[2], dht11_dat[3], f );
#endif
    }
    else
    {
#ifdef DEBUG
        printf( "Data not good, skip\n" );
#endif
    }
}
