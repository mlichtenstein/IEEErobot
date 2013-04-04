# This file synchronizes the ld "Settings.h" with the upper deck "Setting.py"  
# Note that the upper deck file gets overwritten, so make your changes in Settings.h and
# then invoke this makefile.
#
# Invoke it like this: go to directory ud, then enter the commands:
#
# $rm settings.py
# $make Settings

PYSRC=$(wildcard *.py) 
PYSRC2=$(wildcard robot/*.py)
PYSRC3=$(wildcard tg/*.py)

TESTRESULTS=$(PYSRC:%.py=results/doctest%.out) $(PYSRC2:robot/%.py=results/doctest%.out) $(PYSRC3:tg/%.py=results/doctest%.out)

run:
	sed -i "s/\t/    /g" *.py
	python main.py

Debug: Settings

Release: Settings

TestAll: resultsFolder $(TESTRESULTS)
	sed -i "s/\t/    /g" *.py
resultsFolder: 
	mkdir -p results
Settings: settings.py

settings.py: ../ld/Settings.h
	grep "#define ROBOT_" $< | sed "s/\#define\ ROBOT_\(\w*\)\s\(.*\)/\1 = \2/g" > $@

results/doctest%.out: tg/%.py
	python -m doctest -v $< && RET=$? | tee $@ && exit $(RET)
results/doctest%.out: robot/%.py
	python -m doctest -v $< && RET=$? | tee $@ && exit $(RET)
results/doctest%.out: %.py
	python -m doctest -v $< && RET=$? | tee $@ && exit $(RET)
