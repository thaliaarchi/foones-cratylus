#!/bin/bash

TR=-v
RES={_}

#TR=-u
#RES=x

../tools/ss2s.py $1 && \
../tools/s2cr.py ${1/.ss/.s} && \
../tools/simp_cr.py ${1/.ss/.cr} -o ${1/.ss/.simple.cr} ${TR} -t "{Z}" ${RES} && \
../tools/crc.py ${1/.ss/.simple.cr} && \
gcc -o ${1/.ss/.bin} ${1/.ss/.simple.c} -lgmp && \
./${1/.ss/.bin}

#../cratylus.py -s ${1/.ss/.simple.cr}
