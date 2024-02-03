PO_FILES := $(wildcard *.po)
MO_FILES := $(patsubst %.po,%.mo,$(PO_FILES))
LANGUAGES := $(patsubst %.mo,%,$(MO_FILES))
MO_NAME := nautilus-open-any-terminal.mo

all: $(MO_FILES)

$(LANGUAGES): %: %.mo

$(MO_FILES): %.mo: %.po
	msgfmt -o $@ $^

install:
	$(foreach lang,$(LANGUAGES),install -Dm644 $(lang).mo \
	          $(PREFIX)/share/locale/$(lang)/LC_MESSAGES/$(MO_NAME);)

uninstall:
	$(foreach lang,$(LANGUAGES),$(RM) $(PREFIX)/share/locale/$(lang)/LC_MESSAGES/$(MO_NAME);)

clean:
	$(RM) *.mo

.PHONY: all clean install uninstall $(LANGUAGES)
