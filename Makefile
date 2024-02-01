LOCALES := nautilus_open_any_terminal/locale

ifeq ($(shell id -u),0)
export PREFIX ?= /usr
else
export PREFIX ?= ${HOME}/.local
endif

FILE_MANAGERS ?= nautilus caja
EXTSRC := nautilus_open_any_terminal/nautilus_open_any_terminal.py
SCHEMASRC := nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml
SCHEMADEST := $(PREFIX)/share/glib-2.0/schemas


build:
	$(MAKE) -C $(LOCALES)

clean:
	$(MAKE) -C $(LOCALES) clean

install:
	for fm in $(FILE_MANAGERS); do \
	    install -Dm644 $(EXTSRC) -t $(PREFIX)/share/$${fm}-python/extensions; \
	done
	$(MAKE) -C $(LOCALES) install
	install -Dm644 $(SCHEMASRC) -t $(SCHEMADEST)

schema:
	glib-compile-schemas $(SCHEMADEST)

uninstall:
	$(RM) $(foreach fm,$(FILE_MANAGERS),$(PREFIX)/share/$(fm)-python/extensions/$(basename $(EXTSRC)))
	$(MAKE) -C $(LOCALES) uninstall
	$(RM) $(SCHEMADEST)/$(basename $(SCHEMASRC))


.PHONY: build clean install schema uninstall
