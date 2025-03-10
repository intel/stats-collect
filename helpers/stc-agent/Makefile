PREFIX ?= /tmp/stc-agent
BINDIR := $(PREFIX)/bin
TOOLNAMES = stc-agent stc-agent-ipmi-helper stc-agent-proc-interrupts-helper

all:
	

clean:
	

install:
	mkdir -p $(BINDIR)
	cp stc-agent.standalone $(BINDIR)/stc-agent
	cp stc-agent-ipmi-helper.standalone $(BINDIR)/stc-agent-ipmi-helper
	cp stc-agent-proc-interrupts-helper.standalone $(BINDIR)/stc-agent-proc-interrupts-helper

uninstall:
	rm -f $(BINDIR)/stc-agent $(BINDIR)/stc-agent-ipmi-helper $(BINDIR)/stc-agent-proc-interrupts-helper
	rmdir --ignore-fail-on-non-empty $(BINDIR)
