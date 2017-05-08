#include "DHT11.h"

int main(void)
{

    if ( wiringPiSetup() == -1 )
        exit( 1 );
    DHT11Data dh = {0, 0, 0, 0, 0};
    read_dht11_data(&dh, 2);

    return 0;
}
