PROGS=sndfile-to-text sndfile haqpps

CFLAGS+=-lsndfile
CGLAGS+=-Wall
CFLAGS+=-ggdb

all: $(PROGS)

clean:
	rm -f *.o $(PROGS)
