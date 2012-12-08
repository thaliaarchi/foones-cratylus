#!/bin/bash

TR=-v
RES=Z

#TR=-u
#RES=x

../tools/ss2s.py $1 && ../tools/s2cr.py ${1/.ss/.s} && ../tools/simp_cr.py ${1/.ss/.cr} -o ${1/.ss/.simple.cr} ${TR} -t "{Z}" ${RES} && ../cratylus.py -s ${1/.ss/.simple.cr}
