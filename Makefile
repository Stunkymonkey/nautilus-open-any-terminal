LOCALES := nautilus_open_any_terminal/locale

ifeq ($(shell id -u),0)
export PREFIX ?= /usr
else
export PREFIX ?= ${HOME}/.local
endif

EXTSRC := nautilus_open_any_terminal/nautilus_open_any_terminal.py
EXTDEST := $(PREFIX)/share/nautilus-python/extensions
SCHEMASRC := nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml
SCHEMADEST := $(PREFIX)/share/glib-2.0/schemas


DESTDIR ?=

build:
	$(MAKE) -C $(LOCALES)

clean:
	$(MAKE) -C $(LOCALES) clean

install:
	install -Dm644 $(EXTSRC) -t $(DESTDIR)$(EXTDEST)
	$(MAKE) -C $(LOCALES) install
	install -Dm644 $(SCHEMASRC) -t $(DESTDIR)$(SCHEMADEST)

schema:
	glib-compile-schemas $(DESTDIR)$(SCHEMADEST)

uninstall:
	$(RM) $(DESTDIR)$(EXTDEST)/$$(basename $(EXTSRC))
	$(MAKE) -C $(LOCALES) uninstall
	$(RM) $(DESTDIR)$(SCHEMADEST)/$$(basename $(SCHEMASRC))

.PHONY: build clean install schema uninstall
