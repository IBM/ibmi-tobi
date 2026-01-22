define FOOTER
SUBDIRS_$(d) := $(patsubst %/,%,$(addprefix $(d)/,$(SUBDIRS)))


CLEAN_$(d) := $(CLEAN_$(d)) $(filter /%,$(CLEAN) $(TARGETS)) $(addprefix $(d)/,$(filter-out /%,$(CLEAN)))

ifdef TARGETS
TARGETS_$(d) := $(TARGETS)
$(foreach tgt,$(TARGETS),$(eval vpath $(tgt) $(OBJPATH_$(d)))$(eval $(tgt)_d = $(d))$(eval $(call generate_rule,$(tgt),${$(tgt)_SRC},${$(tgt)_DEP},${$(tgt)_RECIPE})))
endif


########################################################################
# Inclusion of subdirectories rules - only after this line one can     #
# refer to subdirectory targets and so on.                             #
########################################################################
$(foreach sd,$(SUBDIRS),$(eval $(call include_subdir_rules,$(sd))))

.PHONY: dir_$(d) clean_$(d) clean_extra_$(d) clean_tree_$(d) dist_clean_$(d)
.SECONDARY: $(OBJPATH)

# Whole tree targets
all :: $(TARGETS_$(d))

clean_all :: clean_$(d)

# dist_clean is optimized in skel.mk if we are building in out of project tree
ifeq ($(strip $(TOP_BUILD_DIR)),)
dist_clean :: dist_clean_$(d)

# No point to enforce clean_extra dependency if CLEAN is empty
ifeq ($(strip $(CLEAN_$(d))),)
dist_clean_$(d) :
else
dist_clean_$(d) : clean_extra_$(d)
endif
	rm -rf $(DIST_CLEAN_DIR)
endif

########################################################################
#                        Per directory targets                         #
########################################################################

clean_$(d) :
	$(info cleaning $(CLEAN_DIR))

clean_tree_$(d) : clean_$(d) $(foreach sd,$(SUBDIRS_$(d)),clean_tree_$(sd))

# Skip the target rules generation and inclusion of the dependencies
# when we just want to clean up things :)
ifeq ($(filter clean clean_% dist_clean,$(MAKECMDGOALS)),)

SUBDIRS_TGTS := $(foreach sd,$(SUBDIRS_$(d)),$(TARGETS_$(sd)))

# Target rules for all "non automatic" targets
# $(foreach tgt,$(filter-out $(AUTO_TGTS),$(TARGETS_$(d))),$(eval $(call tgt_rule,$(tgt))))

# Way to build all targets in given subtree (not just current dir as via
# dir_$(d) - see below)
tree_$(d) : $(TARGETS_$(d)) $(foreach sd,$(SUBDIRS_$(d)),tree_$(sd))

# If the directory is just for grouping its targets will be targets from
# all subdirectories
ifeq ($(strip $(TARGETS_$(d))),)
TARGETS_$(d) := $(SUBDIRS_TGTS)
endif

# This is a default rule - see Makefile
dir_$(d) : $(TARGETS_$(d))

slashify = $(subst _,/,$(1))

.SECONDEXPANSION:
dir_% : dir_$$(TOP)/$$(call slashify,$$(subst dir_,,$$(@)))
	@echo

endif
endef
