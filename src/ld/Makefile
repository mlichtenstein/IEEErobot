# Used for compiling Arduino
include settings.mk
#include ../../AVR-makefile

TESTDIR=test
TESTBINDIR=$(TESTDIR)/bin
TESTRESULTSDIR=$(TESTDIR)/results

TESTSRC=$(wildcard $(TESTDIR)/*.cpp)
TESTRESULTS=$(TESTSRC:$(TESTDIR)/%.cpp=$(TESTRESULTSDIR)/%.out)
TESTBINARY=$(TESTSRC:$(TESTDIR)/%.cpp=$(TESTBINDIR)/%)
TESTDEPEND=$(TESTSRC:$(TESTDIR)/%.cpp=$(TESTDIR)/obj/%.d)
TestAll: Dirs $(TESTDEPEND) $(TESTRESULTS) $(TESTBINARY)

Dirs:
	mkdir -p $(TESTBINDIR)
	mkdir -p $(TESTRESULTSDIR)
	mkdir -p $(TESTDIR)/obj
cleanTestAll: clean
clean::
	rm -rf $(TESTDIR)/obj
	rm -rf $(TESTDIR)/bin
	rm -rf $(TESTDIR)/results

$(TESTRESULTSDIR)/%.out: $(TESTBINDIR)/%
	echo "BEGIN Testing $<"
	$< | tee $@
	echo "END Testing $<"

$(TESTBINDIR)/%: $(TESTDIR)/%.cpp $(wildcard *.h) $(wildcard *.pde)
	g++ -Itest $(SRCCDEF) $(CXXFLAGS) -o $@ $<
#	g++ $(SRCCDEF) $(CXXFLAGS) -I/usr/lib/avr/include -o $@ $<

$(TESTDIR)/obj/%.d: $(TESTDIR)/%.c
	mkdir -p $(shell dirname $@)
	g++ -Itest -M $(ALL_CFLAGS) $< | sed "s;$(notdir $*).o:;$*.o $*.d:;" > $@

$(TESTDIR)/obj/%.d: $(TESTDIR)/%.cpp
	mkdir -p $(shell dirname $@)
	g++ -Itest -M $(ALL_CXXFLAGS) $< | sed "s;$(notdir $*).o:;$*.o $*.d:;" > $@

ifneq ($(MAKECMDGOALS),clean)
include $(TESTDEPEND)
endif
