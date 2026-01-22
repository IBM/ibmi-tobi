SHELL:=/QOpenSys/pkgs/bin/bash
TOBI_PATH:=/QOpenSys/pkgs/lib/tobi
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables
MK := $(TOBI_PATH)/src/mk
SCRIPTSPATH := $(TOBI_PATH)/src/scripts
COLOR_TTY :=
BUILDVARSMKPATH :=

ifndef IBMiRelease
IBMiRelease := $(shell cl 'dspdtaara qgpl/qss1MRI' | /QOpenSys/pkgs/bin/grep 'V[[:digit:]]R[[:digit:]]M[[:digit:]]' -wo | /QOpenSys/pkgs/bin/sed 's/[^0-9]$*//g')
endif

COMPATIBILITYMODE := false
ifeq ($(shell test $(IBMiRelease) -lt 750; echo $$?), 0)
# Older than V7R5M0
COMPATIBILITYMODE := true
endif

ifndef BUILDVARSMKPATH
    $(error BUILDVARSMKPATH is not set)
endif

RUNDIR := $(CURDIR)
ifndef TOP
TOP := $(shell \
       top=$(RUNDIR); \
       while [ ! -r "$$top/iproj.json" ] && [ "$$top" != "" ]; do \
           top=$${top%/*}; \
       done; \
       echo $$top)
endif


.PHONY: dir tree all clean clean_all clean_tree dist_clean

# Default target when nothing is given on the command line.  Reasonable
# options are:
# "dir"  - updates only targets from current directory and its dependencies
# "tree" - updates targets (and their dependencies) in whole subtree
#          starting at current directory
# "all"  - updates all targets in the project
.DEFAULT_GOAL := dir

dir : dir_$(RUNDIR)
tree : tree_$(RUNDIR)

clean : clean_$(RUNDIR)
clean_tree : clean_tree_$(RUNDIR)

# $(d) keeps the path of "current" directory during tree traversal and
# $(dir_stack) is used for backtracking during traversal
d := $(TOP)
dir_stack :=

include $(BUILDVARSMKPATH)
include $(MK)/header.mk
include $(MK)/footer.mk

# Automatic inclusion of the skel.mk at the top level - that way
# Rules.top has exactly the same structure as other Rules.mk
include $(MK)/skel.mk

.SECONDEXPANSION:
$(eval $(value HEADER))
include $(TOP)/.Rules.mk.build
$(eval $(value FOOTER))

# Optional final makefile where you can specify additional targets

# Include all auto-generated source dependency files. Since we don't have a
# hard-coded list of source files, we will grab everything in the `$DEPDIR`
# directory.
-include $(wildcard $(DEPDIR)/*.d)

# This is just a convenience - to let you know when make has stopped
# interpreting make files and started their execution.
# $(info Rules generated $(if $(BUILD_MODE),for "$(BUILD_MODE)" mode,)...)
