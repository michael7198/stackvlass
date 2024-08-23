#!/bin/bash
head -n $1 output.txt | tail -n 1 > foo
sed 's/,/\n/g' foo > bar
wget -i bar
rm foo
rm bar
python3 stack_vlass.py
rm *.ql.*subim.fits
