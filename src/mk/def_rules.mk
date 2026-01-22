COLOR := \033[33;40m
ERROR_COLOR := \033[31;49;1m
SUCCESS_COLOR := \033[32;49;1m
NOCOLOR := \033[0m
ifndef COLOR_TTY
COLOR_TTY := $(shell [ -t 1 ] && echo true)
endif

SYS_ENCODING := $(shell  /QOpenSys/pkgs/bin/python3.9  -c "import sys;print(sys.getdefaultencoding())")
ifndef UTF8_SUPPORT
	ifneq (,$(findstring utf-8,$(SYS_ENCODING)))
		UTF8_SUPPORT := true
	else
		UTF8_SUPPORT := false
	endif
endif

ifeq ($(UTF8_SUPPORT),true)
SUCCESSMARKER = ✓
FAILMARKER = ✕
else
SUCCESSMARKER = [SUCCESS]
FAILMARKER = [FAIL]
endif

ifneq ($(VERBOSE),true)
ifneq ($(strip $(TOP_BUILD_DIR)),)
  strip_top = $(subst $(TOP)/,,$(subst $(TOP_BUILD_DIR)/,,$(1)))
else
  strip_top = $(subst $(TOP)/,,$(1))
endif
ifeq ($(COLOR_TTY),true)
echo_prog := $(shell if echo -e | grep -q -- -e; then echo echo; else echo echo -e; fi)
echo_cmd = $(echo_prog) "$(COLOR)$(call strip_top,$(1))$(NOCOLOR)";
echo_success_cmd = ($(echo_prog) "$(SUCCESS_COLOR)$(SUCCESSMARKER) $(call strip_top,$(1))$(NOCOLOR)" && echo)
echo_error_cmd = ($(echo_prog) "$(ERROR_COLOR)$(FAILMARKER) $(call strip_top,$(1))$(NOCOLOR)" && echo)
else
echo_cmd = @echo "$(call strip_top,$(1))";
echo_success_cmd = (echo "$(SUCCESSMARKER) $(call strip_top,$(1))" && echo)
echo_error_cmd = (echo "$(FAILMARKER) $(call strip_top,$(1))" && echo)
endif
else # Verbose output
echo_cmd =
endif

empty :=
space :=$(empty) $(empty)
uniq = $(if $1,$(firstword $1) $(call uniq,$(filter-out $(firstword $1),$1)))


# The following logs to stdout is parsed and used by the makei program. Check makei.BuildEnv.make before making changes!
define logSuccess =
$(call echo_success_cmd,"$1 was created successfully!")
endef
define logFail =
$(call echo_error_cmd,"Failed to create $1!")
endef

# The extractName and extractTextDescriptor are used to decompose the long filename into module name and
# the text descriptor.
# e.g. CUSTOME1-Customer_file.LF has `CUSTOME1` as the module name and `Customer file` as the text descriptor
define extractName =
echo '$(notdir $<)' | awk -F- '{ print $$1 }'
endef

# Explanation of how extractTextDescriptor works
# removes directory from target filename | substring before the first '.' | substring after the first '-' | replace underscores with spaces
define extractTextDescriptor =
if [[ "$(notdir $<)" == *"-"* ]]; then
	echo '$(notdir $<)' | awk -F. '{print $$1}' | awk -F- '{ i = index($$0,"-");print substr($$0,i+1)}' | sed -e 's/_/ /g';
fi
endef

define genDep
$(eval d = $($(1)_d))$(eval tmpName = $(wildcard $d/$2-*.$3))$(if $(tmpName),$(tmpName),$d/$2.$3)
endef

define getLibPath
 $(addsuffix .LIB,$(addprefix /QSYS.LIB/,$(1)))
endef

ifndef PRECMD
PRECMD :=
endif

ifndef POSTCMD
POSTCMD :=
endif

# define inheritValue
# $(eval k = $1)$(eval d = $2)$(if $($(k)_$(d)),$($(k)_$(d)),$(call inheritValue,$(k),$(realpath $(dir $(d)))))
# endef


# These variables are swapped into the compile commands.  Their values also serve as
# global defaults that can be overridden on a per-object basis by setting target-specific
# variables, e.g. `MYPGM.PGM: private TGTRLS = V7R1M0`.  They can also be overridden on a
# per-object-type basis by setting pattern-specific variables, e.g.
# `%.SRVPGM: private ACTGRP = $(SRVPGM_ACTGRP)` (A variable is used in the assignment
# instead of a constant so that all settings are defined in one place, at the top.)
# tl;dr: If you want to customize a compile setting for an object, change these variables
# in your TARGET (not here).
ifndef ACTGRP
ACTGRP :=
endif
ifndef ALLOW
ALLOW :=
endif
ifndef ALWUPD
ALWUPD := *YES
endif
ifndef AUT
AUT :=
endif
ifndef BNDDIR
BNDDIR :=
endif
ifndef COMMIT
COMMIT := *NONE
endif
ifndef COMPILEOPT
COMPILEOPT :=
endif
ifndef CURLIB
CURLIB :=
endif
ifndef DBGVIEW
DBGVIEW := *ALL
endif
ifndef DBGENCKEY
DBGENCKEY := *NONE
endif
ifndef DEFINE
DEFINE :=
endif
ifndef USRPRF
USRPRF := *USER
endif
ifndef DFRWRT
DFRWRT := *YES
endif
ifndef DETAIL
DETAIL := *EXTENDED
endif
ifndef DFTACTGRP
DFTACTGRP := *NO
endif
ifndef DLTPCT
DLTPCT := *NONE
endif
ifndef ENHDSP
ENHDSP := *YES
endif
ifndef HLPID
HLPID =
endif
ifndef HLPPNLGRP
HLPPNLGRP =
endif
ifndef INLINE
INLINE :=
endif
ifndef LOCALETYPE
LOCALETYPE :=
endif
ifndef OBJTYPE
OBJTYPE :=
endif
ifndef OPTIMIZE
OPTIMIZE :=
endif
ifndef OPTION
OPTION := *EVENTF
endif
ifndef PAGESIZE
PAGESIZE :=
endif
ifndef PGM
PGM :=
endif
ifndef PMTFILE
PMTFILE :=
endif
ifndef PRDLIB
PRDLIB :=
endif
ifndef RCDLEN
RCDLEN :=
endif
ifndef REUSEDLT
REUSEDLT := *NO
endif
ifndef RPGPPOPT
RPGPPOPT :=
endif
ifndef RSTDSP
RSTDSP :=
endif
ifndef SIZE
SIZE :=
endif
ifndef STGMDL
STGMDL := *SNGLVL
endif
ifndef SYSIFCOPT
SYSIFCOPT :=
endif
ifndef TERASPACE
TERASPACE :=
endif
ifndef TEXT
TEXT=$(shell $(extractTextDescriptor))
endif
ifndef TYPE
TYPE :=
endif
ifndef TGTRLS
TGTRLS :=
endif
ifndef USRPRF
USRPRF := *USER
endif
ifndef VLDCKR
VLDCKR :=
endif
ifndef ALWRINZ
ALWRINZ := *YES
endif

TGTCCSID = $(TGTCCSID_$($@_d))

# Object-type-specific defaults.  Not used directly, but copied to the standard ones above and then
# inserted into the compile commands.  Each variable here should also precede its corresponding pattern
# rule as a pattern-specific variable. Change these to alter compile defaults for an entire type of
# object.
BNDC_DBGVIEW := $(DBGVIEW)
BNDC_DBGENCKEY := $(DBGENCKEY)
BNDC_USRPRF := $(USRPRF)
BNDC_INCDIR := $(INCDIR)
BNDC_OPTION := $(OPTION)
BNDC_TGTRLS := $(TGTRLS)

BNDCL_ACTGRP := $(ACTGRP)
BNDCL_AUT := $(AUT)
BNDCL_DBGVIEW := $(DBGVIEW)
BNDCL_DBGENCKEY := $(DBGENCKEY)
BNDCL_USRPRF := $(USRPRF)
BNDCL_DFTACTGRP := $(DFTACTGRP)
BNDCL_INCDIR := $(INCDIR)
BNDCL_OPTION := $(OPTION)
BNDCL_TGTRLS := $(TGTRLS)

BNDRPG_ACTGRP := $(ACTGRP)
BNDRPG_AUT := $(AUT)
BNDRPG_DBGVIEW := $(DBGVIEW)
BNDRPG_DBGENCKEY := $(DBGENCKEY)
BNDRPG_USRPRF := $(USRPRF)
BNDRPG_DFTACTGRP := $(DFTACTGRP)
BNDRPG_INCDIR := $(INCDIR)
BNDRPG_OPTION := $(OPTION)
BNDRPG_TGTRLS := $(TGTRLS)

BNDCBL_ACTGRP := $(ACTGRP)
BNDCBL_AUT := $(AUT)
BNDCBL_DBGVIEW := $(DBGVIEW)
BNDCBL_DBGENCKEY := $(DBGENCKEY)
BNDCBL_USRPRF := $(USRPRF)
BNDCBL_INCDIR := $(INCDIR)
BNDCBL_OPTION := $(OPTION)
BNDCBL_TGTRLS := $(TGTRLS)

CPPMOD_AUT := $(AUT)
CPPMOD_DBGVIEW := $(DBGVIEW)
CPPMOD_DBGENCKEY := $(DBGENCKEY)
CPPMOD_USRPRF := $(USRPRF)
CPPMOD_OPTIMIZE := $(OPTIMIZE)
CPPMOD_OPTION := $(OPTION)
CPPMOD_INCDIR := $(INCDIR)
CPPMOD_INLINE := $(INLINE)
CPPMOD_LOCALETYPE := $(LOCALETYPE)
CPPMOD_STGMDL := *INHERIT
CPPMOD_SYSIFCOPT := *IFS64IO
CPPMOD_TERASPACE := *YES *NOTSIFC
CPPMOD_TGTRLS := $(TGTRLS)

CMD_AUT := $(AUT)
CMD_ALLOW :=$(ALLOW)
CMD_HLPID = $(basename $@)
CMD_HLPPNLGRP = $(basename $@)
CMD_PGM = $(basename $@)
CMD_PMTFILE := *NONE
CMD_VLDCKR := *NONE

CMOD_AUT := $(AUT)
CMOD_DEFINE := $(DEFINE)
CMOD_DBGVIEW := $(DBGVIEW)
CMOD_DBGENCKEY := $(DBGENCKEY)
CMOD_OPTIMIZE := $(OPTIMIZE)
CMOD_OPTION := *EVENTF *SHOWUSR *XREF *AGR
CMOD_INCDIR := $(INCDIR)
CMOD_INLINE := $(INLINE)
CMOD_LOCALETYPE := $(LOCALETYPE)
CMOD_STGMDL := *INHERIT
CMOD_SYSIFCOPT := *IFS64IO
CMOD_TERASPACE := *YES *NOTSIFC
CMOD_TGTRLS := $(TGTRLS)
CMOD_USRPRF := $(USRPRF)

CRTPGM_OPTION := $(OPTION)
ifeq ($(COMPATIBILITYMODE), true)
CRTPGM_OPTION :=
endif

CLMOD_AUT := $(AUT)
CLMOD_DBGVIEW := $(DBGVIEW)
CLMOD_DBGENCKEY := $(DBGENCKEY)
CLMOD_OPTIMIZE := $(OPTIMIZE)
CLMOD_OPTION := $(OPTION)
CLMOD_INCDIR := $(INCDIR)
CLMOD_TGTRLS := $(TGTRLS)

DSPF_AUT := $(AUT)
DSPF_DFRWRT := $(DFRWRT)
DSPF_ENHDSP := $(ENHDSP)
DSPF_OPTION := *EVENTF *SRC *LIST
DSPF_RSTDSP := *YES

LF_AUT := $(AUT)
LF_OPTION := *EVENTF *SRC *LIST

MNU_AUT := $(AUT)
MNU_CURLIB := *NOCHG
MNU_OPTION := *EVENTF *SRC
MNU_PRDLIB := *NOCHG
MNU_TYPE := *UIM

PNLGRP_AUT := $(AUT)
PNLGRP_OPTION := *EVENTF *SRC

PF_AUT := $(AUT)
PF_DLTPCT := $(DLTPCT)
PF_OPTION := *EVENTF *SRC *LIST
PF_REUSEDLT := $(REUSEDLT)
PF_SIZE :=
PF_ALWUPD := $(ALWUPD)

PGM_ACTGRP := $(ACTGRP)
PGM_ALWUPD := $(ALWUPD)
PGM_AUT := $(AUT)
PGM_DETAIL := $(DETAIL)
PGM_OPTION := *EVENTF
PGM_STGMDL := *SNGLVL
PGM_TGTRLS := $(TGTRLS)
PGM_ALWRINZ := $(ALWRINZ)
PGM_USRPRF := $(USRPRF)

CBL_OPTION := *SRCDBG
CBL_INCDIR := $(INCDIR)
CBL_TGTRLS := $(TGTRLS)
RPG_OPTION := *SRCDBG
RPG_TGTRLS := $(TGTRLS)
CL_OPTION := *SRCDBG
CL_TGTRLS := $(TGTRLS)
CL_USRPRF := $(USRPRF)

PRTF_AUT := $(AUT)
PRTF_OPTION := *EVENTF *SRC *LIST
PRTF_PAGESIZE := 66 132

QMQRY_AUT := $(AUT)

RPGMOD_AUT := $(AUT)
RPGMOD_DBGVIEW := $(DBGVIEW)
RPGMOD_DBGENCKEY := $(DBGENCKEY)
RPGMOD_INCDIR := $(INCDIR)
RPGMOD_OPTIMIZE := $(OPTIMIZE)
RPGMOD_OPTION := $(OPTION)
RPGMOD_TGTRLS := $(TGTRLS)

CBLMOD_AUT := $(AUT)
CBLMOD_DBGVIEW := $(DBGVIEW)
CBLMOD_DBGENCKEY := $(DBGENCKEY)
CBLMOD_INCDIR := $(INCDIR)
CBLMOD_OPTIMIZE := $(OPTIMIZE)
CBLMOD_OPTION := $(OPTION)
CBLMOD_TGTRLS := $(TGTRLS)
CBLMOD_USRPRF := $(USRPRF)


SQLCIMOD_DBGVIEW := *SOURCE
SQLCIMOD_DBGENCKEY := $(CMOD_DBGENCKEY)
SQLCIMOD_OBJTYPE := *MODULE
SQLCIMOD_OPTION := $(CMOD_OPTION)
SQLCIMOD_INCDIR := $(INCDIR)
SQLCIMOD_STGMDL := $(CMOD_STGMDL)
SQLCIMOD_SYSIFCOPT := $(CMOD_SYSIFCOPT)
SQLCIMOD_TERASPACE := *YES *TSIFC

SQLCPPIMOD_DBGVIEW := *SOURCE
SQLCPPIMOD_DBGENCKEY := $(CPPMOD_DBGENCKEY)
SQLCPPIMOD_DEFINE := $(DEFINE)
SQLCPPIMOD_INCDIR := $(INCDIR)
SQLCPPIMOD_OBJTYPE := *MODULE
SQLCPPIMOD_OPTION := $(CPPMOD_OPTION)

SQLCIPGM_DBGVIEW := *SOURCE
SQLCIPGM_DBGENCKEY := $(DBGENCKEY)
SQLCIPGM_USRPRF := $(USRPRF)
SQLCIPGM_INCDIR := $(INCDIR)
SQLCIPGM_OBJTYPE := *PGM
SQLCIPGM_OPTION := $(OPTION)

SQLRPGIMOD_DBGVIEW := *SOURCE
SQLRPGIMOD_DBGENCKEY := $(RPGMOD_DBGENCKEY)
SQLRPGIMOD_INCDIR := $(INCDIR)
SQLRPGIMOD_OBJTYPE := *MODULE
SQLRPGIMOD_OPTION := $(RPGMOD_OPTION)
SQLRPGIMOD_RPGPPOPT := *LVL2
SQLRPGIMOD_USRPRF := $(USRPRF)

SQLCBLIMOD_DBGVIEW := *SOURCE
SQLCBLIMOD_DBGENCKEY := $(DBGENCKEY)
SQLCBLIMOD_INCDIR := $(INCDIR)
SQLCBLIMOD_OBJTYPE := *MODULE
SQLCBLIMOD_OPTION := $(OPTION)

SQLRPGIPGM_DBGVIEW := *SOURCE
SQLRPGIPGM_DBGENCKEY := $(DBGENCKEY)
SQLRPGIPGM_USRPRF := $(USRPRF)
SQLRPGIPGM_INCDIR := $(INCDIR)
SQLRPGIPGM_OBJTYPE := *PGM
SQLRPGIPGM_OPTION := $(OPTION)
SQLRPGIPGM_RPGPPOPT := *LVL2

SQLCBLIPGM_DBGVIEW := *SOURCE
SQLCBLIPGM_DBGENCKEY := $(DBGENCKEY)
SQLCBLIPGM_USRPRF := $(USRPRF)
SQLCBLIPGM_INCDIR := $(INCDIR)
SQLCBLIPGM_OBJTYPE := *PGM
SQLCBLIPGM_OPTION := $(OPTION)

SQL_TGTRLS := $(TGTRLS)
SQL_USRPRF := $(USRPRF)


SRVPGM_ACTGRP := *CALLER
SRVPGM_ALWUPD := $(ALWUPD)
SRVPGM_AUT := $(AUT)
SRVPGM_USRPRF := $(USRPRF)
SRVPGM_BNDDIR := *NONE
SRVPGM_DETAIL := *BASIC
SRVPGM_STGMDL := $(STGMDL)
SRVPGM_TGTRLS := $(TGTRLS)
SRVPGM_OPTION :=
SRVPGM_ALWRINZ := $(ALWRINZ)
WSCST_AUT := $(AUT)

# Creation command parameters with variables (the ones listed at the top) for the most common ones.
CRTCLMODFLAGS = AUT($(AUT)) DBGVIEW($(DBGVIEW)) OPTIMIZE($(OPTIMIZE)) DBGENCKEY($(DBGENCKEY))  OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTCMDFLAGS = VLDCKR($(VLDCKR)) PMTFILE($(PMTFILE)) HLPPNLGRP($(HLPPNLGRP)) HLPID($(HLPID)) AUT($(AUT)) ALLOW($(ALLOW)) $(if $(TEXT),TEXT('$(TEXT)'),)
CRTCMODFLAGS = TERASPACE($(TERASPACE)) STGMDL($(STGMDL)) OUTPUT(*PRINT) OPTION($(OPTION)) DBGVIEW($(DBGVIEW)) OPTIMIZE($(OPTIMIZE)) DBGENCKEY($(DBGENCKEY))  \
               SYSIFCOPT($(SYSIFCOPT)) AUT($(AUT)) TEXT('$(subst ','',$(TEXT))') TGTCCSID($(TGTCCSID)) TGTRLS($(TGTRLS)) INLINE($(INLINE)) INCDIR($(INCDIR)) \
               LOCALETYPE($(LOCALETYPE)) DEFINE($(DEFINE))
CRTCPPMODFLAGS = TERASPACE($(TERASPACE)) STGMDL($(STGMDL)) OUTPUT(*PRINT) OPTION($(OPTION)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) OPTIMIZE($(OPTIMIZE)) \
                 SYSIFCOPT($(SYSIFCOPT)) AUT($(AUT)) TEXT('$(subst ','',$(TEXT))') TGTCCSID($(TGTCCSID)) TGTRLS($(TGTRLS)) INLINE($(INLINE)) INCDIR($(INCDIR)) \
                 LOCALETYPE($(LOCALETYPE)) DEFINE($(DEFINE)) USRPRF($(USRPRF))
CRTDSPFFLAGS = ENHDSP($(ENHDSP)) RSTDSP($(RSTDSP)) DFRWRT($(DFRWRT)) AUT($(AUT)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))')
CRTLFFLAGS = AUT($(AUT)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))')
CRTMNUFLAGS = AUT($(AUT)) OPTION($(OPTION)) CURLIB($(CURLIB)) PRDLIB($(PRDLIB)) TEXT('$(subst ','',$(TEXT))') TYPE($(TYPE))
CRTPFFLAGS = AUT($(AUT)) DLTPCT($(DLTPCT)) OPTION($(OPTION)) REUSEDLT($(REUSEDLT)) SIZE($(SIZE)) ALWUPD($(PF_ALWUPD)) TEXT('$(subst ','',$(TEXT))')
CRTPGMFLAGS = ACTGRP($(ACTGRP)) ALWUPD($(ALWUPD)) USRPRF($(USRPRF)) TGTRLS($(TGTRLS)) AUT($(AUT)) DETAIL($(DETAIL)) OPTION($(CRTPGM_OPTION)) STGMDL($(STGMDL)) TEXT('$(subst ','',$(TEXT))') ALWRINZ($(ALWRINZ))
CRTPNLGRPFLAGS = AUT($(AUT)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))')
CRTRPGPGMFLAGS = OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') USRPRF($(USRPRF)) TGTRLS($(TGTRLS))
CRTCBLPGMFLAGS = OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') USRPRF($(USRPRF))  TGTRLS($(TGTRLS))
CRTPRTFFLAGS = AUT($(AUT)) OPTION($(OPTION)) PAGESIZE($(PAGESIZE)) TEXT('$(subst ','',$(TEXT))')
CRTRPGMODFLAGS = AUT($(AUT)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) OPTIMIZE($(OPTIMIZE)) OPTION($(OPTION)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') \
                 TGTCCSID($(TGTCCSID)) TGTRLS($(TGTRLS)) INCDIR($(INCDIR)) DEFINE($(DEFINE))
CRTCBLMODFLAGS = AUT($(AUT)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) OPTIMIZE($(OPTIMIZE)) OPTION($(OPTION)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') \
                 TGTCCSID($(TGTCCSID)) TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTQMQRYFLAGS = AUT($(AUT)) TEXT('$(subst ','',$(TEXT))')
CRTSQLCIFLAGS = COMMIT($(COMMIT)) OBJTYPE($(OBJTYPE)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) \
                USRPRF($(USRPRF)) COMPILEOPT('INCDIR($(doublequotedINCDIR)) OPTION($(OPTION)) STGMDL($(STGMDL)) SYSIFCOPT($(SYSIFCOPT)) \
                           TGTCCSID($(TGTCCSID))  TERASPACE($(TERASPACE)) OPTIMIZE($(OPTIMIZE)) INLINE($(INLINE))') CVTCCSID($(TGTCCSID))
CRTSQLCPPIFLAGS = COMMIT($(COMMIT)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) \
				  USRPRF($(USRPRF)) CVTCCSID($(TGTCCSID)) OPTION($(OPTION)) \
                  COMPILEOPT('STGMDL($(STGMDL)) SYSIFCOPT($(SYSIFCOPT)) DEFINE($(DEFINE)) OPTIMIZE($(OPTIMIZE)) INLINE($(INLINE)) \
                  TGTCCSID($(TGTCCSID))  TERASPACE($(TERASPACE)) INCDIR($(doublequotedINCDIR))')
CRTSQLRPGIFLAGS = COMMIT($(COMMIT)) OBJTYPE($(OBJTYPE)) OPTION($(OPTION)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') \
                  TGTRLS($(TGTRLS)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) RPGPPOPT($(RPGPPOPT)) \
                  COMPILEOPT('TGTCCSID($(TGTCCSID)) OPTIMIZE($(OPTIMIZE)) INCDIR($(doublequotedINCDIR))')
CRTSQLCBLIFLAGS = COMMIT($(COMMIT)) OBJTYPE($(OBJTYPE)) OPTION($(OPTION)) OUTPUT(*PRINT) TEXT('$(subst ','',$(TEXT))') \
                  TGTRLS($(TGTRLS)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) CVTCCSID($(TGTCCSID)) \
                  COMPILEOPT('TGTCCSID($(TGTCCSID)) OPTIMIZE($(OPTIMIZE)) INCDIR($(doublequotedINCDIR))')
CRTSRVPGMFLAGS = ACTGRP($(ACTGRP)) ALWUPD($(ALWUPD)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) AUT($(AUT)) DETAIL($(DETAIL)) STGMDL($(STGMDL)) OPTION($(OPTION)) BNDDIR($(BNDDIR)) USRPRF($(USRPRF)) ALWRINZ($(ALWRINZ))
CRTWSCSTFLAGS = AUT($(AUT)) TEXT('$(subst ','',$(TEXT))')
CRTBNDRPGFLAGS = TGTCCSID($(TGTCCSID)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTBNDCBLFLAGS = TGTCCSID($(TGTCCSID)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTBNDCFLAGS = TGTCCSID($(TGTCCSID)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTBNDCLFLAGS = AUT($(AUT)) DBGVIEW($(DBGVIEW)) DBGENCKEY($(DBGENCKEY)) USRPRF($(USRPRF)) OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) INCDIR($(INCDIR))
CRTCLPGMFLAGS = OPTION($(OPTION)) TEXT('$(subst ','',$(TEXT))') TGTRLS($(TGTRLS)) USRPRF($(USRPRF))
RUNSQLFLAGS = DBGVIEW(*SOURCE) TGTRLS($(TGTRLS)) OUTPUT(*PRINT) MARGINS(1024) COMMIT($(COMMIT))

# Extra command string for adhoc addition of extra parameters to a creation command.
ADHOCCRTFLAGS =

# Miscellaneous variables
SRCPATH := $(TOP)
OBJPATH = $(OBJPATH_$($@_d))
CURLIB :=
# IBMiEnvCmd :=
# override OBJPATH = $(shell echo "$(OBJPATH)" | tr '[:lower:]' '[:upper:]')
OBJLIB = $(basename $(notdir $(OBJPATH)))
LIBL = $(call ESCAPE_FOR_RECIPE,$(OBJLIB))
# preUsrlibl :=
# postUsrlibl :=
TOOLSPATH := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TOOLSLIB := BOBTOOLS
runDate := $(shell date +"%F_%H.%M.%S-%a")
LOGPATH := $(TOP)/.logs
LOGFILE := $(LOGPATH)/output.log
JOBLOGFILE := $(LOGPATH)/joblog.json
$(shell mkdir -p $(LOGPATH))
# $(info IBMiMake log directory: $(LOGPATH))
DEPDIR := $(SRCPATH)/.deps
$(shell mkdir -p $(DEPDIR) >/dev/null)
EVTDIR := $(SRCPATH)/.evfevent
$(shell mkdir -p $(EVTDIR) >/dev/null)
CRTFRMSTMFLIB := CRTFRMSTMF
ICONV := /QOpenSys/usr/bin/iconv
ICONV_EBCDIC := IBM-037
ICONV_ASCII := UTF-8
SETCCSID_ASCII := 1208
PREUSRLIBLPATH = $(call getLibPath,$(preUsrlibl))
POSTUSRLIBLPATH = $(call getLibPath,$(postUsrlibl))
CURLIBPATH = $(call getLibPath,$(curlib))

VPATH = $(subst $(space),:,$(strip $(call uniq,$(strip $(unquotedINCDIR)) $(PREUSRLIBLPATH) $(CURLIBPATH) $(POSTUSRLIBLPATH) $(OBJPATH) $(SRCPATH))))


define PRESETUP =
echo -e "$(crtcmd)"; \
curlib="$(curlib)" \
preUsrlibl="$(preUsrlibl)" \
postUsrlibl="$(postUsrlibl)" \
IBMiEnvCmd="$(IBMiEnvCmd)" \
$(eval directory := $(subst /,_,$(patsubst $(SRCPATH)/%,%,$(dir $<)))) \
$(eval directory := $(if $(filter ._,$(directory)),,$(directory))) \
$(eval file := $(subst .,_,$(notdir $@))) \
$(eval logFile := $(LOGPATH)/$(directory)$(file).splf)
endef

define SETCURLIBTOOBJLIB =
tmpCurlib="$(call ESCAPE_FOR_RECIPE,$(OBJLIB))"
endef

define ESCAPE_FOR_RECIPE
$(subst #,\#,$(1))
endef

define SHELL_VALUE_OBJLIB
$(subst $(H),\$(H),$1)
endef

# cleanCDeps removes from the CRTCMOD-generated dependency file any header files located in /QIBM/, plus the
# original .C file that is included for some reason, and adds the correct suffix to the target (SO1001 -> SO1001.MODULE).
cleanCDeps = awk '$$2 !~ /^\/QIBM\// && $$2 !~ /$(notdir $<)$$/ && $$2 !~ /$(basename $(notdir $<)).MBR$$/ { sub("^.*/","",$$2); sub("^$*","$@",$$1); print $$1 " " toupper($$2) }'

# This defines the steps taken after a C compile to massage the auto-generated dependencies into a useable form.
# See http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/#tldr
define POSTCCOMPILE =

endef

# cleanRPGDeps removes from the CRTRPGMOD- and CRTSQLRPGI-generated events file any system header files
# plus any SQL precompiler-generated source member, and returns what's left.
cleanRPGDeps = awk '$$1 == "FILEID" && $$6 !~ /^QTEMP/ && toupper($$6) !~ /QSYS/ && $$6 !~ /EVFTEMPF0[12]/ && $$6 !~ /$(basename $(notdir $<)).MBR$$/ { print toupper($$6) }'

# This defines the steps taken after an RPG compile to scrape dependencies from the EVFEVENT file and turn them
# into a useable form.
# See http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/#tldr
# In a nutshell, retrieve the flattened list of include files from the EVFEVENT file, then for each one discover
# if any externally-described files are declared.  If so, isolate the actual source file name from its path,
# convert everything to upper case, format in makefile dependency format, and output all these dependencies
# to a file that will be included by Make.
# - The above is not being done at this time
#  parm is name of local evfevent file (might have .PGM.eventf suffix)
define EVFEVENT_DOWNLOAD =
system "CPYTOSTMF FROMMBR('$(OBJPATH)/EVFEVENT.FILE/$(basename $@).MBR') TOSTMF('$(EVTDIR)/$1') STMFCCSID(1208) ENDLINFMT(*LF) CVTDTA(*AUTO) STMFOPT(*REPLACE)" >/dev/null
endef
# define POSTRPGCOMPILE =
# $(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent.evfevent);
# endef

# Deletes .d dependency file if it's empty.
define removeEmptyDep =
if [ ! -s $(DEPDIR)/$(basename $@).d ]; then \
  rm $(DEPDIR)/$(basename $@).d; \
fi
endef


# Can't specify our default ACTGRP value if DFTACTGRP(*YES) is specified.
derive_ACTGRP = $(if $(filter *YES,$(DFTACTGRP)),,$(ACTGRP))

# Insure that the CCSID attribute of a source file matches what we know its encoding to be.  This attribute
# gets reset to a default value each time a file is placed into the IFS.  The attribute must match the actual
# encoding in order for compile commands that support stream files to work.  Only attempt setting IFS files.
define set_STMF_CCSID =
-setccsid $(SETCCSID_ASCII) $(filter-out /QSYS.LIB/%,$(realpath $^))
endef

# These variables allow pattern-specific variables to be used when multiple source patterns exist for one object pattern (like with *FILEs, which can be PFs, LFs, DSPFs, etc.).
# The pattern-specific variable will set itself to a variable below, which will then be evaluated
# from the context of that pattern-matched rule. This can be used to set specific compile parameters
# for each type of, for example, file object (PF, LF, DSPF, etc.).
# The advantage of this approach over simply hard-coding values in the recipe is that individual targets (compiled objects)
# will be able to override these values with their own, thereby overriding these defaults.
# This elaborate construct is to work around a limitation in Make (`%.object: %.source variable=value` does not work; it
# effectively resolves to `%.object: variable=value`).
#
# Determine default settings for the various source types that can make a file object.
fileAUT = $(strip \
	$(if $(filter %.DSPF,$<),$(DSPF_AUT), \
	$(if $(filter %.dspf,$<),$(DSPF_AUT), \
	$(if $(filter %.LF,$<),$(LF_AUT), \
	$(if $(filter %.lf,$<),$(LF_AUT), \
	$(if $(filter %.PF,$<),$(PF_AUT), \
	$(if $(filter %.pf,$<),$(PF_AUT), \
	$(if $(filter %.PRTF,$<),$(PRTF_AUT), \
	$(if $(filter %.prtf,$<),$(PRTF_AUT), \
	UNKNOWN_FILE_TYPE)))))))))
fileDFRWRT = $(strip \
	$(if $(filter %.DSPF,$<),$(DSPF_DFRWRT), \
	$(if $(filter %.dspf,$<),$(DSPF_DFRWRT), \
	UNKNOWN_FILE_TYPE)))
fileENHDSP = $(strip \
	$(if $(filter %.DSPF,$<),$(DSPF_ENHDSP), \
	$(if $(filter %.dspf,$<),$(DSPF_ENHDSP), \
	UNKNOWN_FILE_TYPE)))
fileDLTPCT = $(strip \
	$(if $(filter %.PF,$<),$(PF_DLTPCT), \
	$(if $(filter %.pf,$<),$(PF_DLTPCT), \
	UNKNOWN_FILE_TYPE)))
fileOPTION = $(strip \
	$(if $(filter %.DSPF,$<),$(DSPF_OPTION), \
	$(if $(filter %.dspf,$<),$(DSPF_OPTION), \
	$(if $(filter %.LF,$<),$(LF_OPTION), \
	$(if $(filter %.lf,$<),$(LF_OPTION), \
	$(if $(filter %.PF,$<),$(PF_OPTION), \
	$(if $(filter %.pf,$<),$(PF_OPTION), \
	$(if $(filter %.PRTF,$<),$(PRTF_OPTION), \
	$(if $(filter %.prtf,$<),$(PRTF_OPTION), \
	UNKNOWN_FILE_TYPE)))))))))
filePAGESIZE = $(strip \
	$(if $(filter %.PRTF,$<),$(PRTF_PAGESIZE), \
	$(if $(filter %.prtf,$<),$(PRTF_PAGESIZE), \
	UNKNOWN_FILE_TYPE)))
fileREUSEDLT = $(strip \
	$(if $(filter %.PF,$<),$(PF_REUSEDLT), \
	$(if $(filter %.pf,$<),$(PF_REUSEDLT), \
	UNKNOWN_FILE_TYPE)))
fileRSTDSP = $(strip \
	$(if $(filter %.DSPF,$<),$(DSPF_RSTDSP), \
	$(if $(filter %.dspf,$<),$(DSPF_RSTDSP), \
	UNKNOWN_FILE_TYPE)))
fileSIZE = $(strip \
	$(if $(filter %.PF,$<),$(PF_SIZE), \
	$(if $(filter %.pf,$<),$(PF_SIZE), \
	UNKNOWN_FILE_TYPE)))
fileALWUPD = $(strip \
	$(if $(filter %.PF,$<),$(PF_ALWUPD), \
	$(if $(filter %.pf,$<),$(PF_ALWUPD), \
	UNKNOWN_FILE_TYPE)))
fileTGTRLS = $(strip \
	$(if $(filter %.table,$<),$(SQL_TGTRLS), \
	$(if $(filter %.TABLE,$<),$(SQL_TGTRLS), \
	$(if $(filter %.pfsql,$<),$(SQL_TGTRLS), \
	$(if $(filter %.PFSQL,$<),$(SQL_TGTRLS), \
	$(if $(filter %.view,$<),$(SQL_TGTRLS), \
	$(if $(filter %.VIEW,$<),$(SQL_TGTRLS), \
	$(if $(filter %.index,$<),$(SQL_TGTRLS), \
	$(if $(filter %.INDEX,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqludt,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLUDT,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlalias,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLALIAS,$<),$(SQL_TGTRLS), \
	UNKNOWN_FILE_TYPE)))))))))))))

# Determine default settings for the various source types that can make a module object.
moduleAUT = $(strip \
	$(if $(filter %.C,$<),    $(CMOD_AUT), \
	$(if $(filter %.c,$<),    $(CMOD_AUT), \
	$(if $(filter %.CPP,$<),  $(CPPMOD_AUT), \
	$(if $(filter %.cpp,$<),  $(CPPMOD_AUT), \
	$(if $(filter %.CLLE,$<), $(CLMOD_AUT), \
	$(if $(filter %.clle,$<), $(CLMOD_AUT), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_AUT), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_AUT), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_AUT), \
	$(if $(filter %.cblle,$<),$(CBLMOD_AUT), \
	UNKNOWN_FILE_TYPE)))))))))))
moduleDBGVIEW = $(strip \
	$(if $(filter %.C,$<),$(CMOD_DBGVIEW), \
	$(if $(filter %.c,$<),$(CMOD_DBGVIEW), \
	$(if $(filter %.CPP,$<),$(CPPMOD_DBGVIEW), \
	$(if $(filter %.cpp,$<),$(CPPMOD_DBGVIEW), \
	$(if $(filter %.CLLE,$<),$(CLMOD_DBGVIEW), \
	$(if $(filter %.clle,$<),$(CLMOD_DBGVIEW), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_DBGVIEW), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_DBGVIEW), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_DBGVIEW), \
	$(if $(filter %.cblle,$<),$(CBLMOD_DBGVIEW), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_DBGVIEW), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_DBGVIEW), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_DBGVIEW), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_DBGVIEW), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_DBGVIEW), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_DBGVIEW), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_DBGVIEW), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_DBGVIEW), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))
moduleDBGENCKEY = $(strip \
	$(if $(filter %.C,$<),$(CMOD_DBGENCKEY), \
	$(if $(filter %.c,$<),$(CMOD_DBGENCKEY), \
	$(if $(filter %.CPP,$<),$(CPPMOD_DBGENCKEY), \
	$(if $(filter %.cpp,$<),$(CPPMOD_DBGENCKEY), \
	$(if $(filter %.CLLE,$<),$(CLMOD_DBGENCKEY), \
	$(if $(filter %.clle,$<),$(CLMOD_DBGENCKEY), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_DBGENCKEY), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_DBGENCKEY), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_DBGENCKEY), \
	$(if $(filter %.cblle,$<),$(CBLMOD_DBGENCKEY), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_DBGENCKEY), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_DBGENCKEY), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_DBGENCKEY), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_DBGENCKEY), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_DBGENCKEY), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_DBGENCKEY), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_DBGENCKEY), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_DBGENCKEY), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))
moduleDEFINE = $(strip \
	$(if $(filter %.C,$<),    $(CMOD_DEFINE), \
	$(if $(filter %.c,$<),    $(CMOD_DEFINE), \
	$(if $(filter %.CPP,$<),  $(CPPMOD_DEFINE), \
	$(if $(filter %.cpp,$<),  $(CPPMOD_DEFINE), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_DEFINE), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_DEFINE), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_DEFINE), \
	$(if $(filter %.cblle,$<),$(CBLMOD_DEFINE), \
	UNKNOWN_FILE_TYPE)))))))))
moduleOPTIMIZE = $(strip \
	$(if $(filter %.C,$<),    $(CMOD_OPTIMIZE), \
	$(if $(filter %.c,$<),    $(CMOD_OPTIMIZE), \
	$(if $(filter %.CPP,$<),  $(CPPMOD_OPTIMIZE), \
	$(if $(filter %.cpp,$<),  $(CPPMOD_OPTIMIZE), \
	$(if $(filter %.CLLE,$<), $(CLMOD_OPTIMIZE), \
	$(if $(filter %.clle,$<), $(CLMOD_OPTIMIZE), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_OPTIMIZE), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_OPTIMIZE), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_OPTIMIZE), \
	$(if $(filter %.cblle,$<),$(CBLMOD_OPTIMIZE), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_OPTIMIZE), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_OPTIMIZE), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_OPTIMIZE), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_OPTIMIZE), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_OPTIMIZE), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_OPTIMIZE), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_OPTIMIZE), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_OPTIMIZE), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))
moduleOBJTYPE = $(strip \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_OBJTYPE), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_OBJTYPE), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_OBJTYPE), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_OBJTYPE), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_OBJTYPE), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_OBJTYPE), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_OBJTYPE), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_OBJTYPE), \
	UNKNOWN_FILE_TYPE)))))))))
moduleOPTION = $(strip \
	$(if $(filter %.C,$<),$(CMOD_OPTION), \
	$(if $(filter %.c,$<),$(CMOD_OPTION), \
	$(if $(filter %.CPP,$<),$(CPPMOD_OPTION), \
	$(if $(filter %.cpp,$<),$(CPPMOD_OPTION), \
	$(if $(filter %.CLLE,$<),$(CLMOD_OPTION), \
	$(if $(filter %.clle,$<),$(CLMOD_OPTION), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_OPTION), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_OPTION), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_OPTION), \
	$(if $(filter %.cblle,$<),$(CBLMOD_OPTION), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_OPTION), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_OPTION), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_OPTION), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_OPTION), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_OPTION), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_OPTION), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_OPTION), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_OPTION), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))
moduleINCDIR = $(strip \
	$(if $(filter %.C,$<),$(CMOD_INCDIR), \
	$(if $(filter %.c,$<),$(CMOD_INCDIR), \
	$(if $(filter %.CPP,$<),$(CPPMOD_INCDIR), \
	$(if $(filter %.cpp,$<),$(CPPMOD_INCDIR), \
	$(if $(filter %.CLLE,$<),$(CLMOD_INCDIR), \
	$(if $(filter %.clle,$<),$(CLMOD_INCDIR), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_INCDIR), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_INCDIR), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_INCDIR), \
	$(if $(filter %.cblle,$<),$(CBLMOD_INCDIR), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_INCDIR), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_INCDIR), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIMOD_INCDIR), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIMOD_INCDIR), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_INCDIR), \
	$(if $(filter %.cblle,$<),$(CBLMOD_INCDIR), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_INCDIR), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_INCDIR), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_INCDIR), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_INCDIR), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))))
moduleINLINE = $(strip \
	$(if $(filter %.C,$<),    $(CMOD_INLINE), \
	$(if $(filter %.c,$<),    $(CMOD_INLINE), \
	$(if $(filter %.CPP,$<),  $(CPPMOD_INLINE), \
	$(if $(filter %.cpp,$<),  $(CPPMOD_INLINE), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_INLINE), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_INLINE), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_INLINE), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_INLINE), \
	UNKNOWN_FILE_TYPE)))))))))
moduleLOCALETYPE = $(strip \
	$(if $(filter %.C,$<),    $(CMOD_LOCALETYPE), \
	$(if $(filter %.c,$<),    $(CMOD_LOCALETYPE), \
	$(if $(filter %.CPP,$<),  $(CPPMOD_LOCALETYPE), \
	$(if $(filter %.cpp,$<),  $(CPPMOD_LOCALETYPE), \
	UNKNOWN_FILE_TYPE)))))
moduleRPGPPOPT = $(strip \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_RPGPPOPT), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_RPGPPOPT), \
	UNKNOWN_FILE_TYPE)))
moduleSTGMDL = $(strip \
	$(if $(filter %.C,$<),$(CMOD_STGMDL), \
	$(if $(filter %.c,$<),$(CMOD_STGMDL), \
	$(if $(filter %.CPP,$<),$(CPPMOD_STGMDL), \
	$(if $(filter %.cpp,$<),$(CPPMOD_STGMDL), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_STGMDL), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_STGMDL), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_STGMDL), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_STGMDL), \
	UNKNOWN_FILE_TYPE)))))))))
moduleSYSIFCOPT = $(strip \
	$(if $(filter %.C,$<),$(CMOD_SYSIFCOPT), \
	$(if $(filter %.c,$<),$(CMOD_SYSIFCOPT), \
	$(if $(filter %.CPP,$<),$(CPPMOD_SYSIFCOPT), \
	$(if $(filter %.cpp,$<),$(CPPMOD_SYSIFCOPT), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_SYSIFCOPT), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_SYSIFCOPT), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_SYSIFCOPT), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_SYSIFCOPT), \
	UNKNOWN_FILE_TYPE)))))))))
moduleTERASPACE = $(strip \
	$(if $(filter %.C,$<),$(CMOD_TERASPACE), \
	$(if $(filter %.c,$<),$(CMOD_TERASPACE), \
	$(if $(filter %.CPP,$<),$(CPPMOD_TERASPACE), \
	$(if $(filter %.cpp,$<),$(CPPMOD_TERASPACE), \
	$(if $(filter %.SQLC,$<),$(SQLCIMOD_TERASPACE), \
	$(if $(filter %.sqlc,$<),$(SQLCIMOD_TERASPACE), \
	$(if $(filter %.SQLCPP,$<),$(SQLCPPIMOD_TERASPACE), \
	$(if $(filter %.sqlcpp,$<),$(SQLCPPIMOD_TERASPACE), \
	UNKNOWN_FILE_TYPE)))))))))
moduleTGTRLS = $(strip \
	$(if $(filter %.C,$<),$(CMOD_TGTRLS), \
	$(if $(filter %.c,$<),$(CMOD_TGTRLS), \
	$(if $(filter %.CPP,$<),$(CPPMOD_TGTRLS), \
	$(if $(filter %.cpp,$<),$(CPPMOD_TGTRLS), \
	$(if $(filter %.CLLE,$<),$(CLMOD_TGTRLS), \
	$(if $(filter %.clle,$<),$(CLMOD_TGTRLS), \
	$(if $(filter %.RPGLE,$<),$(RPGMOD_TGTRLS), \
	$(if $(filter %.rpgle,$<),$(RPGMOD_TGTRLS), \
	$(if $(filter %.CBLLE,$<),$(CBLMOD_TGTRLS), \
	$(if $(filter %.cblle,$<),$(CBLMOD_TGTRLS), \
	$(if $(filter %.SQLC,$<),$(CMOD_TGTRLS), \
	$(if $(filter %.sqlc,$<),$(CMOD_TGTRLS), \
	$(if $(filter %.SQLCPP,$<),$(CPPMOD_TGTRLS), \
	$(if $(filter %.sqlcpp,$<),$(CPPMOD_TGTRLS), \
	$(if $(filter %.SQLRPGLE,$<),$(RPGMOD_TGTRLS), \
	$(if $(filter %.sqlrpgle,$<),$(RPGMOD_TGTRLS), \
	$(if $(filter %.SQLCBLLE,$<),$(CBLMOD_TGTRLS), \
	$(if $(filter %.sqlcblle,$<),$(CBLMOD_TGTRLS), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))
moduleUSRPRF = $(strip \
	$(if $(filter %.C,$<),$(CMOD_USRPRF), \
	$(if $(filter %.c,$<),$(CMOD_USRPRF), \
	$(if $(filter %.CPP,$<),$(CPPMOD_USRPRF), \
	$(if $(filter %.cpp,$<),$(CPPMOD_USRPRF), \
	$(if $(filter %.SQLC,$<),$(CMOD_USRPRF), \
	$(if $(filter %.sqlc,$<),$(CMOD_USRPRF), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIMOD_USRPRF), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIMOD_USRPRF), \
	$(if $(filter %.SQLCBLLE,$<),$(CBLMOD_USRPRF), \
	$(if $(filter %.sqlcblle,$<),$(CBLMOD_USRPRF), \
	$(if $(filter %.SQLCPP,$<),$(CPPMOD_USRPRF), \
	$(if $(filter %.sqlcpp,$<),$(CPPMOD_USRPRF), \
	UNKNOWN_FILE_TYPE)))))))))))))

# Determine default settings for the various source types that can make a program object.
programACTGRP = $(strip \
	$(if $(filter %.CLLE,$<),$(BNDCL_ACTGRP), \
	$(if $(filter %.clle,$<),$(BNDCL_ACTGRP), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_ACTGRP), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_ACTGRP), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_ACTGRP), \
	$(if $(filter %.cblle,$<),$(BNDCBL_ACTGRP), \
	$(if $(filter %.MODULE,$<),$(PGM_ACTGRP), \
	$(if $(filter %.module,$<),$(PGM_ACTGRP), \
	UNKNOWN_FILE_TYPE)))))))))
programALWUPD = $(strip \
	$(if $(filter %.MODULE,$<),$(PGM_ALWUPD), \
	$(if $(filter %.module,$<),$(PGM_ALWUPD), \
	UNKNOWN_FILE_TYPE)))
programAUT = $(strip \
	$(if $(filter %.CLLE,$<),$(BNDCL_AUT), \
	$(if $(filter %.clle,$<),$(BNDCL_AUT), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_AUT), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_AUT), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_AUT), \
	$(if $(filter %.cblle,$<),$(BNDCBL_AUT), \
	$(if $(filter %.MODULE,$<),$(PGM_AUT), \
	$(if $(filter %.module,$<),$(PGM_AUT), \
	UNKNOWN_FILE_TYPE)))))))))
programDBGVIEW = $(strip \
	$(if $(filter %.C,$<),$(BNDC_DBGVIEW), \
	$(if $(filter %.c,$<),$(BNDC_DBGVIEW), \
	$(if $(filter %.CLLE,$<),$(BNDCL_DBGVIEW), \
	$(if $(filter %.clle,$<),$(BNDCL_DBGVIEW), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_DBGVIEW), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_DBGVIEW), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_DBGVIEW), \
	$(if $(filter %.cblle,$<),$(BNDCBL_DBGVIEW), \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_DBGVIEW), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_DBGVIEW), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_DBGVIEW), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_DBGVIEW), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIPGM_DBGVIEW), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIPGM_DBGVIEW), \
	UNKNOWN_FILE_TYPE)))))))))))))))
programDBGENCKEY = $(strip \
	$(if $(filter %.C,$<),$(BNDC_DBGENCKEY), \
	$(if $(filter %.c,$<),$(BNDC_DBGENCKEY), \
	$(if $(filter %.CLLE,$<),$(BNDCL_DBGENCKEY), \
	$(if $(filter %.clle,$<),$(BNDCL_DBGENCKEY), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_DBGENCKEY), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_DBGENCKEY), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_DBGENCKEY), \
	$(if $(filter %.cblle,$<),$(BNDCBL_DBGENCKEY), \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_DBGENCKEY), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_DBGENCKEY), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_DBGENCKEY), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_DBGENCKEY), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIPGM_DBGENCKEY), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIPGM_DBGENCKEY), \
	UNKNOWN_FILE_TYPE)))))))))))))))
programUSRPRF = $(strip \
	$(if $(filter %.C,$<),$(BNDC_USRPRF), \
	$(if $(filter %.c,$<),$(BNDC_USRPRF), \
	$(if $(filter %.CLLE,$<),$(BNDCL_USRPRF), \
	$(if $(filter %.clle,$<),$(BNDCL_USRPRF), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_USRPRF), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_USRPRF), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_USRPRF), \
	$(if $(filter %.cblle,$<),$(BNDCBL_USRPRF), \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_USRPRF), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_USRPRF), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_USRPRF), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_USRPRF), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIPGM_USRPRF), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIPGM_USRPRF), \
	$(if $(filter %.MODULE,$<),$(PGM_USRPRF), \
	$(if $(filter %.module,$<),$(PGM_USRPRF), \
	$(if $(filter %.RPG,$<),$(PGM_USRPRF), \
	$(if $(filter %.rpg,$<),$(PGM_USRPRF), \
	$(if $(filter %.CLP,$<),$(CL_USRPRF), \
	$(if $(filter %.clp,$<),$(CL_USRPRF), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))))
programDETAIL = $(strip \
	$(if $(filter %.MODULE,$<),$(PGM_DETAIL), \
	$(if $(filter %.module,$<),$(PGM_DETAIL), \
	UNKNOWN_FILE_TYPE)))
programDFTACTGRP = $(strip \
	$(if $(filter %.CLLE,$<),$(BNDCL_DFTACTGRP), \
	$(if $(filter %.clle,$<),$(BNDCL_DFTACTGRP), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_DFTACTGRP), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_DFTACTGRP), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_DFTACTGRP), \
	$(if $(filter %.cblle,$<),$(BNDCBL_DFTACTGRP), \
	UNKNOWN_FILE_TYPE)))))))
programOBJTYPE = $(strip \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_OBJTYPE), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_OBJTYPE), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_OBJTYPE), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_OBJTYPE), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIPGM_OBJTYPE), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIPGM_OBJTYPE), \
	UNKNOWN_FILE_TYPE)))))))
programOPTION = $(strip \
	$(if $(filter %.C,$<),$(BNDC_OPTION), \
	$(if $(filter %.c,$<),$(BNDC_OPTION), \
	$(if $(filter %.CLLE,$<),$(BNDCL_OPTION), \
	$(if $(filter %.clle,$<),$(BNDCL_OPTION), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_OPTION), \
	$(if $(filter %.cblle,$<),$(BNDCBL_OPTION), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_OPTION), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_OPTION), \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_OPTION), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_OPTION), \
	$(if $(filter %.SQLCBLLE,$<),$(SQLCBLIPGM_OPTION), \
	$(if $(filter %.sqlcblle,$<),$(SQLCBLIPGM_OPTION), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_OPTION), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_OPTION), \
	$(if $(filter %.MODULE,$<),$(PGM_OPTION), \
	$(if $(filter %.module,$<),$(PGM_OPTION), \
	$(if $(filter %.CBL,$<),$(CBL_OPTION), \
	$(if $(filter %.cbl,$<),$(CBL_OPTION), \
	$(if $(filter %.RPG,$<),$(RPG_OPTION), \
	$(if $(filter %.rpg,$<),$(RPG_OPTION), \
	$(if $(filter %.CLP,$<),$(CL_OPTION), \
	$(if $(filter %.clp,$<),$(CL_OPTION), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))))))
programRPGPPOPT = $(strip \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_RPGPPOPT), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_RPGPPOPT), \
	UNKNOWN_FILE_TYPE)))
programSTGMDL = $(strip \
	$(if $(filter %.MODULE,$<),$(PGM_STGMDL), \
	$(if $(filter %.module,$<),$(PGM_STGMDL), \
	UNKNOWN_FILE_TYPE)))
programTGTRLS = $(strip \
	$(if $(filter %.C,$<),$(BNDC_TGTRLS), \
	$(if $(filter %.c,$<),$(BNDC_TGTRLS), \
	$(if $(filter %.CLLE,$<),$(BNDCL_TGTRLS), \
	$(if $(filter %.clle,$<),$(BNDCL_TGTRLS), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_TGTRLS), \
	$(if $(filter %.cblle,$<),$(BNDCBL_TGTRLS), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_TGTRLS), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_TGTRLS), \
	$(if $(filter %.SQLC,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlc,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLCBLLE,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlcblle,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLRPGLE,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlrpgle,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLPRC,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlprc,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLTRG,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqltrg,$<),$(SQL_TGTRLS), \
	$(if $(filter %.MODULE,$<),$(PGM_TGTRLS), \
	$(if $(filter %.module,$<),$(PGM_TGTRLS), \
	$(if $(filter %.CBL,$<),$(CBL_TGTRLS), \
	$(if $(filter %.cbl,$<),$(CBL_TGTRLS), \
	$(if $(filter %.RPG,$<),$(RPG_TGTRLS), \
	$(if $(filter %.rpg,$<),$(RPG_TGTRLS), \
	$(if $(filter %.CLP,$<),$(CL_TGTRLS), \
	$(if $(filter %.clp,$<),$(CL_TGTRLS), \
	UNKNOWN_FILE_TYPE)))))))))))))))))))))))))))
programINCDIR = $(strip \
	$(if $(filter %.C,$<),$(BNDC_INCDIR), \
	$(if $(filter %.c,$<),$(BNDC_INCDIR), \
	$(if $(filter %.CLLE,$<),$(BNDCL_INCDIR), \
	$(if $(filter %.clle,$<),$(BNDCL_INCDIR), \
	$(if $(filter %.RPGLE,$<),$(BNDRPG_INCDIR), \
	$(if $(filter %.rpgle,$<),$(BNDRPG_INCDIR), \
	$(if $(filter %.CBLLE,$<),$(BNDCBL_INCDIR), \
	$(if $(filter %.cblle,$<),$(BNDCBL_INCDIR), \
	$(if $(filter %.SQLC,$<),$(SQLCIPGM_INCDIR), \
	$(if $(filter %.sqlc,$<),$(SQLCIPGM_INCDIR), \
	$(if $(filter %.SQLRPGLE,$<),$(SQLRPGIPGM_INCDIR), \
	$(if $(filter %.sqlrpgle,$<),$(SQLRPGIPGM_INCDIR), \
	UNKNOWN_FILE_TYPE)))))))))))))

# Determine default settings for the various source types that can make a srvpgm object.
srvpgmTGTRLS = $(strip \
	$(if $(filter %.BND,$<),$(SRVPGM_TGTRLS), \
	$(if $(filter %.bnd,$<),$(SRVPGM_TGTRLS), \
	$(if $(filter %.ILESRVPGM,$<),$(SRVPGM_TGTRLS), \
	$(if $(filter %.ilesrvpgm,$<),$(SRVPGM_TGTRLS), \
	$(if $(filter %.SQLUDF,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqludf,$<),$(SQL_TGTRLS), \
	$(if $(filter %.SQLVAR,$<),$(SQL_TGTRLS), \
	$(if $(filter %.sqlvar,$<),$(SQL_TGTRLS), \
	UNKNOWN_FILE_TYPE)))))))))

#    ____ __  __ ____    ____           _
#   / ___|  \/  |  _ \  |  _ \ ___  ___(_)_ __   ___  ___
#  | |   | |\/| | | | | | |_) / _ \/ __| | '_ \ / _ \/ __|
#  | |___| |  | | |_| | |  _ <  __/ (__| | |_) |  __/\__ \
#   \____|_|  |_|____/  |_| \_\___|\___|_| .__/ \___||___/
#                                        |_|

define CMDSRC_TO_CMD_RECIPE =
	$(eval AUT = $(CMD_AUT))
	$(eval ALLOW = $(CMD_ALLOW))
	$(eval HLPID = $(CMD_HLPID))
	$(eval HLPPNLGRP = $(CMD_HLPPNLGRP))
	$(eval PMTFILE = $(CMD_PMTFILE))
	$(eval VLDCKR = $(CMD_VLDCKR))
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating command [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTCMD CMD($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) \
        srcstmf('$<') PGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB)/$(CMD_PGM))) $(CRTCMDFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile)> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@);
endef
define CMD_TO_CMD_RECIPE =
	$(eval AUT = $(CMD_AUT))
	$(eval ALLOW = $(CMD_ALLOW))
	$(eval HLPID = $(CMD_HLPID))
	$(eval HLPPNLGRP = $(CMD_HLPPNLGRP))
	$(eval PMTFILE = $(CMD_PMTFILE))
	$(eval VLDCKR = $(CMD_VLDCKR))
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating command [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTCMD CMD($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') PGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB)/$(CMD_PGM))) $(CRTCMDFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile)> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@);
endef



#   _____ ___ _     _____   ____           _
#  |  ___|_ _| |   | ____| |  _ \ ___  ___(_)_ __   ___  ___
#  | |_   | || |   |  _|   | |_) / _ \/ __| | '_ \ / _ \/ __|
#  |  _|  | || |___| |___  |  _ <  __/ (__| | |_) |  __/\__ \
#  |_|   |___|_____|_____| |_| \_\___|\___|_| .__/ \___||___/
#                                           |_|

define FILE_VARIABLES =
	$(eval AUT = $(fileAUT))\
	$(eval DFRWRT = $(fileDFRWRT))\
	$(eval DLTPCT = $(fileDLTPCT))\
	$(eval ENHDSP = $(fileENHDSP))\
	$(eval OPTION = $(fileOPTION))\
	$(eval PAGESIZE = $(filePAGESIZE))\
	$(eval REUSEDLT = $(fileREUSEDLT))\
	$(eval RSTDSP = $(fileRSTDSP))\
	$(eval SIZE = $(fileSIZE))\
	$(eval TGTRLS = $(fileTGTRLS))\
	$(eval ALWUPD = $(fileALWUPD))\
	$(eval TYPEDEF = $(if $(filter YES,$(CREATE_TYPEDEF)),$(SCRIPTSPATH)/crttypedef "$<" "$@" "$(OBJPATH)",))
endef

define DSPF_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating DSPF [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTDSPF" -p $(CRTDSPFFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTDSPF" -p "$(CRTDSPFFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define LF_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating LF [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTLF" -p $(CRTLFFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTLF" -p "$(CRTLFFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
	@$(TYPEDEF)
endef

define PF_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	@$(call echo_cmd,"=== Creating PF [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPF" -p $(CRTPFFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPF" -p "$(CRTPFFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
	@$(TYPEDEF)
endef

define PRTF_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating PRTF [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPRTF" -p $(CRTPRTFFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPRTF" -p "$(CRTPRTFFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
	@$(TYPEDEF)
endef

# @$(TOOLSPATH)/checkObjectAlreadyExists $@ $(OBJLIB)
# @$(TOOLSPATH)/checkIfBuilt $@ $(OBJLIB)
define TABLE_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL TABLE $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

# @$(TOOLSPATH)/checkObjectAlreadyExists $@ $(OBJLIB)
# @$(TOOLSPATH)/checkIfBuilt $@ $(OBJLIB)
define PFSQL_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL PFSQL $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

# @$(TOOLSPATH)/checkObjectAlreadyExists $@ $(OBJLIB)
# @$(TOOLSPATH)/checkIfBuilt $@ $(OBJLIB)
define VIEW_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL VIEW $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define INDEX_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL INDEX $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define SQLUDT_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL UDT $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define SQLALIAS_TO_FILE_RECIPE =
	$(FILE_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL ALIAS $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*FILE) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef


#   ____ _____  _        _    ____      _      ____           _
#  |  _ \_   _|/ \      / \  |  _ \    / \    |  _ \ ___  ___(_)_ __   ___  ___
#  | | | || | / _ \    / _ \ | |_) |  / _ \   | |_) / _ \/ __| | '_ \ / _ \/ __|
#  | |_| || |/ ___ \  / ___ \|  _ <  / ___ \  |  _ <  __/ (__| | |_) |  __/\__ \
#  |____/ |_/_/   \_\/_/   \_\_| \_\/_/   \_\ |_| \_\___|\___|_| .__/ \___||___/
#                                                              |_|

define DTAARA_VARIABLES =
	$(eval TGTRLS = $(SQL_TGTRLS))
endef

define SQLSEQ_TO_DTAARA_RECIPE =
	$(DTAARA_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL SEQUENCE $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*DTAARA) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

#   __  __ _____ _   _ _   _   ____           _
#  |  \/  | ____| \ | | | | | |  _ \ ___  ___(_)_ __   ___  ___
#  | |\/| |  _| |  \| | | | | | |_) / _ \/ __| | '_ \ / _ \/ __|
#  | |  | | |___| |\  | |_| | |  _ <  __/ (__| | |_) |  __/\__ \
#  |_|  |_|_____|_| \_|\___/  |_| \_\___|\___|_| .__/ \___||___/
#                                              |_|

define MENU_VARIABLES =
	$(eval AUT = $(MNU_AUT))
	$(eval OPTION = $(MNU_OPTION))
	$(eval CURLIB = $(MNU_CURLIB))
	$(eval PRDLIB = $(MNU_PRDLIB))
	$(eval TYPE = $(MNU_TYPE))
endef

define MENUSRC_TO_MENU_RECIPE =
	$(MENU_VARIABLES)
	$(eval d = $($@_d))
	$(eval RCDLEN = 268)
	@$(call echo_cmd,"=== Creating menu [$(notdir $<)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTMNU" -r $(RCDLEN)  -p $(CRTMNUFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTMNU" -r $(RCDLEN) -p "$(CRTMNUFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

#   __  __  ___  ____  _   _ _     _____   ____           _
#  |  \/  |/ _ \|  _ \| | | | |   | ____| |  _ \ ___  ___(_)_ __   ___  ___
#  | |\/| | | | | | | | | | | |   |  _|   | |_) / _ \/ __| | '_ \ / _ \/ __|
#  | |  | | |_| | |_| | |_| | |___| |___  |  _ <  __/ (__| | |_) |  __/\__ \
#  |_|  |_|\___/|____/ \___/|_____|_____| |_| \_\___|\___|_| .__/ \___||___/
#                                                          |_|

define MODULE_VARIABLES
	$(eval AUT = $(moduleAUT))\
	$(eval DBGVIEW = $(moduleDBGVIEW))\
	$(eval DBGENCKEY = $(moduleDBGENCKEY))\
	$(eval OBJTYPE = $(moduleOBJTYPE))\
	$(eval OPTION = $(moduleOPTION))\
	$(eval OPTIMIZE = $(moduleOPTIMIZE))\
	$(eval INCDIR = $(moduleINCDIR))\
	$(eval RPGPPOPT = $(moduleRPGPPOPT))\
	$(eval STGMDL = $(moduleSTGMDL))\
	$(eval SYSIFCOPT = $(moduleSYSIFCOPT))\
	$(eval TERASPACE = $(moduleTERASPACE))\
	$(eval TGTRLS = $(moduleTGTRLS))\
	$(eval USRPRF = $(moduleUSRPRF))
endef

define C_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating C module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtcmod module($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTCMODFLAGS) $(ADHOCCRTFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile)> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@($(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent); ret=$$?; rm $(DEPDIR)/$*.Td 2>/dev/null; exit $$ret)
	@$(POSTCCOMPILE)
endef

# CRTCPPMOD is special because it launches PASE and can't be run in a PASE job so we
# spawn a job and lose the ability to get joblog info
define CPP_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating CPP module [$(notdir $<)] Note environment and library list are not set up")
	$(eval crtcmd := crtcppmod module($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTCMODFLAGS) $(ADHOCCRTFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)"  "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "Y"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@($(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent); ret=$$?; rm $(DEPDIR)/$*.Td 2>/dev/null; exit $$ret)
	@$(POSTCCOMPILE)
endef

define RPGLE_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)\
	@$(call echo_cmd,"=== Creating RPG module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtrpgmod module($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTRPGMODFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define CLLE_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating CL module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCLMOD" -p $(CRTCLMODFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCLMOD" -p "$(CRTCLMODFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define SQLC_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating SQLC module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtsqlci obj($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTSQLCIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@($(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent); ret=$$?; rm $(DEPDIR)/$*.Td 2>/dev/null;  exit $$ret)
endef

define SQLCPP_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating SQLCPP module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtsqlcppi obj($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTSQLCPPIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@($(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent); ret=$$?; rm $(DEPDIR)/$*.Td 2>/dev/null;  exit $$ret)
endef

define SQLRPGLE_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating SQLRPGLE module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtsqlrpgi obj($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTSQLRPGIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(notdir $<).evfevent)
endef

define CBLLE_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating ILE COBOL module [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := crtcblmod module($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTCBLMODFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define SQLCBLLE_TO_MODULE_RECIPE =
	$(MODULE_VARIABLES)
	@$(call echo_cmd,"=== Creating SQLCBLLE module [$(notdir $<)]$(ECHOCCSID)")
	$(eval crtcmd := crtsqlcbli obj($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) srcstmf('$<') $(CRTSQLCBLIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(notdir $<).evfevent)
endef

#   ____   ____ __  __   ____           _
#  |  _ \ / ___|  \/  | |  _ \ ___  ___(_)_ __   ___  ___
#  | |_) | |  _| |\/| | | |_) / _ \/ __| | '_ \ / _ \/ __|
#  |  __/| |_| | |  | | |  _ <  __/ (__| | |_) |  __/\__ \
#  |_|    \____|_|  |_| |_| \_\___|\___|_| .__/ \___||___/
#                                        |_|

define PGM_VARIABLES =
$(eval ACTGRP = $(programACTGRP)) \
$(eval ALWUPD = $(programALWUPD))
$(eval AUT = $(programAUT)) \
$(eval DBGVIEW = $(programDBGVIEW)) \
$(eval DBGENCKEY = $(programDBGENCKEY)) \
$(eval USRPRF = $(programUSRPRF)) \
$(eval DETAIL = $(programDETAIL)) \
$(eval DFTACTGRP = $(programDFTACTGRP)) \
$(eval OBJTYPE = $(programOBJTYPE)) \
$(eval OPTION = $(programOPTION)) \
$(eval RPGPPOPT = $(programRPGPPOPT)) \
$(eval STGMDL = $(programSTGMDL)) \
$(eval TGTRLS = $(programTGTRLS)) \
$(eval INCDIR = $(programINCDIR)) \
$(eval ALWRINZ = $(ALWRINZ)) \
$(eval BNDSRVPGMPATH = $(basename $(filter %.SRVPGM,$(notdir $^)) $(externalsrvpgms)))
endef

define SQLPRC_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating SQL PROCEDURE $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*PGM) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define SQLTRG_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating SQL TRIGGER $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd :=  CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*PGM) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef


define PGM.RPGLE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating Bound RPG Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTBNDRPG srcstmf('$<') PGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) $(CRTBNDRPGFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $@).PGM.evfevent)
endef

define PGM.SQLRPGLE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating Bound SQLRPGLE Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTSQLRPGI srcstmf('$<') OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) $(CRTSQLRPGIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $@).PGM.evfevent)
endef

define PGM.C_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating Bound C Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTBNDC srcstmf('$<') PGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) $(CRTBNDCFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).PGM.evfevent)
endef

define CBL_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating COBOL Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCBLPGM" -p $(CRTCBLPGMFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCBLPGM" -p "$(CRTCBLPGMFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define PGM.CBLLE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating COBOL Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := CRTBNDCBL srcstmf('$<') PGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) $(CRTBNDCBLFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).PGM.evfevent)
endef

define PGM.SQLCBLLE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating Bound SQLCBLLE Program [$(basename $@)] in $(call ESCAPE_FOR_RECIPE,$(OBJLIB))")
	$(eval crtcmd := crtsqlcbli srcstmf('$<') OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) $(CRTSQLCBLIFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $@).PGM.evfevent)
endef

define PGM.CLLE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating ILE CL Program [$(basename $@)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTBNDCL" -p $(CRTBNDCLFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTBNDCL" -p "$(CRTBNDCLFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define CLP_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating OPM CL Program [$(basename $@)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCLPGM" -p $(CRTCLPGMFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTCLPGM" -p "$(CRTCLPGMFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define RPG_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating RPG Program [$(basename $@)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTRPGPGM" -p $(CRTRPGPGMFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTRPGPGM" -p "$(CRTRPGPGMFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(basename $(@F)).evfevent)
endef

define ILEPGM_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating program [$(tgt)] from Pseudo Source [$(basename $(notdir $<))]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define MODULE_TO_PGM_RECIPE =
	$(PGM_VARIABLES)
	@$(call echo_cmd,"=== Creating program [$(tgt)] from modules [$(basename $(filter %.MODULE,$(notdir $^)))] and service programs [$(basename $(filter %.SRVPGM,$(notdir $^$|)))]")
	$(eval externalsrvpgms := $(filter %.SRVPGM,$(subst .LIB,,$(subst /QSYS.LIB/,,$|))))
	$(eval crtcmd := crtpgm pgm($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) module($(basename $(filter %.MODULE,$(notdir $^)))) bndsrvpgm($(if $(BNDSRVPGMPATH),$(BNDSRVPGMPATH),*NONE)) $(CRTPGMFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
	@$(call EVFEVENT_DOWNLOAD,$(tgt).PGM.evfevent)
endef

#   ____  _   _ _     ____ ____  ____    ____           _
#  |  _ \| \ | | |   / ___|  _ \|  _ \  |  _ \ ___  ___(_)_ __   ___  ___
#  | |_) |  \| | |  | |  _| |_) | |_) | | |_) / _ \/ __| | '_ \ / _ \/ __|
#  |  __/| |\  | |__| |_| |  _ <|  __/  |  _ <  __/ (__| | |_) |  __/\__ \
#  |_|   |_| \_|_____\____|_| \_\_|     |_| \_\___|\___|_| .__/ \___||___/
#                                                        |_|

define PNLGRP_VARIABLES =
	$(eval AUT = $(PNLGRP_AUT))
	$(eval OPTION = $(PNLGRP_OPTION))
endef

define PNLGRPSRC_TO_PNLGRP_RECIPE =
	$(PNLGRP_VARIABLES)
	$(eval d = $($@_d))
	$(eval RCDLEN = 268)
	@$(call echo_cmd,"=== Creating panel group [$(basename $@)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPNLGRP" -r $(RCDLEN) -p $(CRTPNLGRPFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTPNLGRP" -r $(RCDLEN) -p "$(CRTPNLGRPFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef



#   ____  ______     ______   ____ __  __   ____           _
#  / ___||  _ \ \   / /  _ \ / ___|  \/  | |  _ \ ___  ___(_)_ __   ___  ___
#  \___ \| |_) \ \ / /| |_) | |  _| |\/| | | |_) / _ \/ __| | '_ \ / _ \/ __|
#   ___) |  _ < \ V / |  __/| |_| | |  | | |  _ <  __/ (__| | |_) |  __/\__ \
#  |____/|_| \_\ \_/  |_|    \____|_|  |_| |_| \_\___|\___|_| .__/ \___||___/
#                                                           |_|

define SRVPGM_VARIABLES =
	$(eval ACTGRP = $(SRVPGM_ACTGRP))\
	$(eval AUT = $(SRVPGM_AUT))\
	$(eval USRPRF = $(SRVPGM_USRPRF))\
	$(eval DETAIL = $(SRVPGM_DETAIL))\
	$(eval ALWUPD = $(SRVPGM_ALWUPD))\
	$(eval STGMDL = $(SRVPGM_STGMDL))\
	$(eval TGTRLS = $(srvpgmTGTRLS))\
	$(eval OPTION = $(SRVPGM_OPTION))\
	$(eval ALWRINZ = $(SRVPGM_ALWRINZ))\
	$(eval BNDSRVPGMPATH = $(basename $(filter %.SRVPGM,$(notdir $^)) $(externalsrvpgms)))
endef

define SQLUDF_TO_SRVPGM_RECIPE =
	$(SRVPGM_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating SQL UDF $(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@)) from Sql statement [$(notdir $<)]")
	$(eval tempFile := $(shell mktemp))
	$(eval crtcmd := RUNSQLSTM srcstmf('$(tempFile)') $(RUNSQLFLAGS))
	$(eval mbrtextcmd := CHGOBJD OBJ($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(notdir $@))) OBJTYPE(*SRVPGM) TEXT('$(subst ','',$(TEXT))'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/extractPseudoSQLAndLaunch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" $(logFile) "$(mbrtextcmd)" "$(VPATH)" "$(tempFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define BND_TO_SRVPGM_RECIPE =
	$(SRVPGM_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating service program [$(tgt)] from modules [$(basename $(filter %.MODULE,$(notdir $^)))] and service programs [$(basename $(filter %.SRVPGM,$(notdir $^$|)))]")
	$(eval externalsrvpgms := $(filter %.SRVPGM,$(subst .LIB,,$(subst /QSYS.LIB/,,$|))))
	$(eval crtcmd := CRTSRVPGM srcstmf('$<') SRVPGM($(call ESCAPE_FOR_RECIPE,$(OBJLIB))/$(basename $(@F))) MODULE($(basename $(filter %.MODULE,$(notdir $^)))) BNDSRVPGM($(if $(BNDSRVPGMPATH),$(BNDSRVPGMPATH),*NONE)) $(CRTSRVPGMFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define ILESRVPGM_TO_SRVPGM_RECIPE =
	$(SRVPGM_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating service program [$(tgt)] from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define SQLVAR_TO_SRVPGM_RECIPE =
    $(SRVPGM_VARIABLES)
    $(eval d = $($@_d))
    @$(call echo_cmd,"=== Creating SQL Global Variable [$(notdir $<)]")
    $(eval crtcmd := RUNSQLSTM srcstmf('$<') $(RUNSQLFLAGS))
    @$(PRESETUP) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" "" "$(mbrtextcmd)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

#    ___ _____ _   _ _____ ____    ____           _
#   / _ \_   _| | | | ____|  _ \  |  _ \ ___  ___(_)_ __   ___  ___
#  | | | || | | |_| |  _| | |_) | | |_) / _ \/ __| | '_ \ / _ \/ __|
#  | |_| || | |  _  | |___|  _ <  |  _ <  __/ (__| | |_) |  __/\__ \
#   \___/ |_| |_| |_|_____|_| \_\ |_| \_\___|\___|_| .__/ \___||___/
#                                                  |_|


define BNDDIR_TO_BNDDIR_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating BND from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define DTAARA_TO_DTAARA_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating DTAARA from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define DTAQ_TO_DTAQ_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating DTAQ from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef


define SYSTRG_TO_TRG_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating System TRG from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define SQL_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Running SQL Statement from [$(notdir $<)]")
	$(eval crtcmd := RUNSQLSTM srcstmf('$<'))
	@$(PRESETUP) \
	$(SETCURLIBTOOBJLIB) \
	$(SCRIPTSPATH)/launch "$(JOBLOGFILE)" "$(crtcmd)" "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)"> $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define MSGF_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating Message from [$(notdir $<)]")
	$(eval crtcmd := $(shell $(SCRIPTSPATH)/extractPseudoSrc $< '$(value OBJLIB)' $(basename $(@F))))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/extractAndLaunch "$(JOBLOGFILE)" "$<" $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) $(basename $(@F)) "$(PRECMD)" "$(POSTCMD)" "$(notdir $@)" "$<" "$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define WSCST_VARIABLES =
	$(eval AUT = $(WSCST_AUT))
endef

define WSCSTSRC_TO_WSCST_RECIPE =
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating work station customizing object [$(tgt)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID)  -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB))
	-c "CRTWSCST" -p $(CRTWSCSTFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTWSCST" -p "$(CRTWSCSTFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

define QMQRY_VARIABLES =
	$(eval AUT = $(QMQRY_AUT))
endef

define SQL_TO_QMQRY_RECIPE =
	$(QMQRY_VARIABLES)
	$(eval d = $($@_d))
	@$(call echo_cmd,"=== Creating QM query [$(basename $@)]")
	$(eval crtcmd := $(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTQMQRY" -p $(CRTQMQRYFLAGS))
	@$(PRESETUP) \
	$(SCRIPTSPATH)/crtfrmstmf --ccsid $(TGTCCSID) -f $< -o $(basename $(@F)) -l $(call ESCAPE_FOR_RECIPE,$(OBJLIB)) -c "CRTQMQRY" -p "$(CRTQMQRYFLAGS)" --save-joblog "$(JOBLOGFILE)" --precmd="$(PRECMD)" --postcmd="$(POSTCMD)" --output="$(logFile)" > $(logFile) 2>&1 && $(call logSuccess,$@) || $(call logFail,$@)
endef

# $(DEPDIR)/%.d: ;
# .PRECIOUS: $(DEPDIR)/%.d

# The *.rebuild file is used as a way of controlling the rebuild of items whose
# rebuild scripts are external to Make.
# Example:
#    THIRDPARTY.SRVPGM: $(DEPDIR)/THIRDPARTY.SRVPGM.rebuild
#        build_thirdparty.sh
#    MYPGM.PGM: MYPGM.MODULE THIRDPARTY.SRVPGM
# 'THIRDPARTY.SRVPGM' is built outside of our Makefile, so Make has no way of knowing
# when its source code has changed and it should be recompiled.  If we
# executed the recipe every time, it would cause all items dependent on it to
# also be rebuilt.  By making the 3rd-party item dependent on this dummy .rebuild
# file, we can cause its recipe to normally not run, and we can force its recipe
# to run by manually `touch`ing its .rebuild file.
# The following rule causes the initial .rebuild file to be automatically created.
# $(DEPDIR)/%.rebuild:
# 	@touch $@


.PHONY: version
version: ; @echo "Make version: $(MAKE_VERSION)"


.PHONY: test
test:
	@echo "SHELL:			$(SHELL)"; \
	echo ".SHELLFLAGS:		$(.SHELLFLAGS)"; \
	echo "CURDIR:			$(CURDIR)"; \
	echo "SRCPATH:		$(SRCPATH)"; \
	echo "OBJPATH:		$(OBJPATH)"; \
	echo "OBJLIB:			$(call ESCAPE_FOR_RECIPE,$(OBJLIB))"; \
	echo "LIBL:			$(call ESCAPE_FOR_RECIPE,$(OBJLIB))"; \
	echo "IBMiEnvCmd:		$(IBMiEnvCmd)"; \
	echo "IBMiRelease:		$(IBMiRelease)"; \
	echo "COMPATIBILITYMODE:$(COMPATIBILITYMODE)"; \
	echo "INCDIR:           $(INCDIR)"; \
	echo "preUsrlibl:		$(preUsrlibl)"; \
	echo "postUsrlibl:		$(postUsrlibl)"; \
	echo "ScriptPath:		$(SCRIPTPATH)"; \
	echo "TOOLSPATH:		$(TOOLSPATH)"; \
	echo "PROJECTDIR:		$(PROJECTDIR)";

# Definition of variable ${\n} containing just new-line character
define \\n


endef
