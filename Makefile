LOCALES := nautilus_open_any_terminal/locale

ifneq ($(shell id -u),0)
export DESTDIR ?= ${HOME}
endif

ifeq ($(DESTDIR),${HOME})
export PREFIX ?= /.local
endif
export PREFIX ?= /usr

DEST := $(DESTDIR)$(PREFIX)
EXTSRC := nautilus_open_any_terminal/nautilus_open_any_terminal.py
SCHEMASRC := nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml
SCHEMADEST := $(DEST)/share/glib-2.0/schemas

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
	install -Dm644 $(EXTSRC) -t $(DEST)/share/$(patsubst install-%,%-python,$@)/extensions

install-common:
	$(MAKE) -C $(LOCALES) install
	install -Dm644 $(SCHEMASRC) -t $(SCHEMADEST)

uninstall: $(UNINSTALLS)

$(UNINSTALLS): uninstall-common
	$(RM) $(DEST)/share/$(patsubst uninstall-%,%-python,$@)/extensions/$(notdir $(EXTSRC))

uninstall-common:
	$(MAKE) -C $(LOCALES) uninstall
	$(RM) $(SCHEMADEST)/$(notdir $(SCHEMASRC))


.PHONY: build clean schema install $(INSTALLS) install-common uninstall $(UNINSTALLS) uninstall-common
