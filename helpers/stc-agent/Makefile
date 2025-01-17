PREFIX ?= /tmp/stc-agent
BINDIR := $(PREFIX)/bin
TOOLNAMES = stc-agent ipmi-helper proc-interrupts-helper

all:
	

clean:
	

install:
	mkdir -p $(BINDIR)
	cp stc-agent.standalone $(BINDIR)/stc-agent
	cp ipmi-helper.standalone $(BINDIR)/ipmi-helper
	cp proc-interrupts-helper.standalone $(BINDIR)/proc-interrupts-helper

uninstall:
	rm -f $(BINDIR)/stc-agent $(BINDIR)/ipmi-helper $(BINDIR)/proc-interrupts-helper
	rmdir --ignore-fail-on-non-empty $(BINDIR)
