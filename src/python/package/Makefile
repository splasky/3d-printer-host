cc=gcc
CFLAGS=-Wall -Wextra -std=c11 -O3 -g -DNDEBUG -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security  
LDFLAGS=-L/usr/lib/python2.7/config-x86_64-linux-gnu -L/usr/lib -lpython2.7 -lpthread -ldl  -lutil -lm -lwiringPi  -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions -fPIC
INSTDIR=/usr/local/bin
INCLUDE=-I. -I/usr/include/python2.7 -I/usr/include/x86_64-linux-gnu/python2.7 


OBJECTS=DHT11.o



all:makelib
%.o: %.c
	$(CC) $(CFLAGS) $< $(INCLUDE) -c  $(LDFLAGS)
makelib:$(OBJECTS)
	$(CC) $(CFLAGS) -shared -o DHT11.so $(OBJECTS) $(LDFLAGS)


.PHONY: clean

clean:
	rm *.o *.so
