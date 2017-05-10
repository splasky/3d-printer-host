#include "DHT11.h"
#include <stdio.h>
#include <wiringPi.h>

int main(void)
{

    if (wiringPiSetup() == -1) {
        perror("setup error");
        exit(1);
    }

    DHT11Data dh = { 0, 0, 0, 0, 0 };
    int i = 0;
    while (i < 200) {
        if (!read_dht11_data(&dh, 2)) {

            printf("Humidity = %d.%d %% Temperature = %d.%d *C \n", dh.humidity,
                dh.humidityfloat, dh.temperature, dh.temperaturefloat);
            ++i;
        }
        delay(500);
    }

    return 0;
}
