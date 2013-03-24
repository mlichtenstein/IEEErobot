# This file synchronizes the ld "Settings.h" with the upper deck "Setting.py"  
# Note that the upper deck file gets overwritten, so make your changes in Settings.h and
# then invoke this makefile.
#
# Invoke it like this: go to directory ud, then enter the commands:
#
# $rm settings.py
# $make Settings

PYSRC=$(wildcard *.py)

TESTRESULTS=$(PYSRC:%.py=test%.out)

run:
	sed -i "s/\t/    /g" *.py
	python modes.py

Debug: Settings

Release: Settings

TestAll: Settings $(TESTRESULTS)
	sed -i "s/\t/    /g" *.py

Settings: settings.py

settings.py: ../ld/Settings.h
	grep "#define ROBOT_" $< | sed "s/\#define\ ROBOT_\(\w*\)\s\(.*\)/\1 = \2/g" > $@

test%.out: %.py
	python -m doctest -v $< && RET=$? | tee $@ && exit $(RET)
