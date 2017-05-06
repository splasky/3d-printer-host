#include "DHT11.h"

int main(void)
{

    if ( wiringPiSetup() == -1 )
        exit( 1 );
    DHT11Data dh;
    read_dht11_data(&dh);

    return 0;
}
