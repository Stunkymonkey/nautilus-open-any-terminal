LOCALES := nautilus_open_any_terminal/locale

ifeq ($(shell id -u),0)
export PREFIX ?= /usr
else
export PREFIX ?= ${HOME}/.local
endif

EXTSRC := nautilus_open_any_terminal/nautilus_open_any_terminal.py
SCHEMASRC := nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml
SCHEMADEST := $(PREFIX)/share/glib-2.0/schemas

FILE_MANAGERS := nautilus caja
INSTALLS := $(patsubst %,install-%,$(FILE_MANAGERS))
UNINSTALLS := $(patsubst %,uninstall-%,$(FILE_MANAGERS))

build:
	$(MAKE) -C $(LOCALES)

clean:
	$(MAKE) -C $(LOCALES) clean

schema:
	glib-compile-schemas $(SCHEMADEST)

install: $(INSTALLS)

$(INSTALLS): install-common
	install -Dm644 $(EXTSRC) -t $(PREFIX)/share/$(patsubst install-%,%-python,$@)/extensions

install-common:
	$(MAKE) -C $(LOCALES) install
	install -Dm644 $(SCHEMASRC) -t $(SCHEMADEST)

uninstall: $(UNINSTALLS)

$(UNINSTALLS): uninstall-common
	$(RM) $(PREFIX)/share/$(patsubst uninstall-%,%-python,$@)/extensions/$(notdir $(EXTSRC))

uninstall-common:
	$(MAKE) -C $(LOCALES) uninstall
	$(RM) $(SCHEMADEST)/$(notdir $(SCHEMASRC))


.PHONY: build clean schema install $(INSTALLS) install-common uninstall $(UNINSTALLS) uninstall-common
