TOP := $(dir $(CURDIR)/$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST)))

BUILD := $(TOP)/build
FSW_BINARY := $(BUILD)/bin/Linux/rpi
FSW_DICTIONARY := $(BUILD)/Rpi/Top/RpiTopologyAppDictionary.xml

SEQ_DIR := $(TOP)/seq
BIN_DIR := $(BUILD)/seq
SEQUENCES := $(wildcard $(SEQ_DIR)/*.seq)

# Compiled sequences should sit in build/seq/*.bin
COMPILED_SEQUENCES := $(addprefix $(BIN_DIR)/,$(notdir $(SEQUENCES:.seq=.bin)))

$(BIN_DIR)/%.bin: $(SEQ_DIR)/%.seq $(FSW_DICTIONARY) $(BIN_DIR)
	fprime-seqgen --dictionary $(FSW_DICTIONARY) $< $@

seqs: $(COMPILED_SEQUENCES)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

sync: seqs
	for seqbin in $(COMPILED_SEQUENCES) ; do \
		scp $$seqbin rpi:/seq/$(basename $$seqbin) ; \
	done

clean:
	rm $(COMPILED_SEQUENCES)


.PHONY: clean sync seqs
