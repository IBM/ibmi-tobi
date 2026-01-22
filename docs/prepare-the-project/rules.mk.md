# Defining Targets using Rules.mk

> [!NOTE]
>
> This page documents how to create a `Rules.mk`, which is a text file that tells TOBi how your project structured and what the objects are.

## Overview

The Object Builder uses GNU Make to determine what code needs to be compiled. Make takes as input a _makefile_, which tells it what objects should be compiled, what source code they need, and what other objects they are dependent on. In TOBi, we will reuse a common Makefile in the TOBi directory which reads the `Rules.mk` files dynamically in the project.

By itself, Make has no concept of ILE objects, and doesn't know how to compile an RPG module or bind together a service program.  The Object Builder provides that functionality in the makefile `mk/def_rules.mk`,  which contains all the special instructions for building various types of IBM i objects. That way, when your `Rules.mk` says "build module XY1001 from source file XY1001.RPGLE", Make will know how to do that.

Each directory of your project that contains source will have its own `Rules.mk` file specific that directory's source.  This allows you to decompose your application into logical units that can be built together or independently.

## Rules.mk layout

The `Rules.mk` consists of two sections:

- Optional _subdirs_ declaration
- A _rules_ area that lists each object that should be built and from which source file. Optionally information about other dependencies and custom compile settings can be specified.

## Creating the Rules.mk

> [!TIP]
>
> You are about to create a `Rules.mk` to describe the objects TOBi should build.  If a project directory doesn't yet exist, [create one](prepare-the-project/create-a-new-project) now.

Create a new `Rules.mk` in your project directory.  Open it in any text editor.

### Subdirs declaration

In this optional section, you may declare that one or more subdirectories is also part of this project and they may contain some objects to build.

For example:

```makefile
SUBDIRS = functionsVAT QDDSSRC QDTASRC QPNLSRC QCLSRC QMSGSRC QRPGSRC QRPGLESRC QCBLSRC QSRVSRC QILESRVSRC QBNDSRC QILESRC QCMDSRC QSQLSRC
```

This line at the project root directory will tell TOBi to build all the subdirectories under the [tobi-example](https://github.com/edmundreinhardt/tobi-example).

### Rules section

The rules section specifies dependency information and custom compile settings. This is where TOBi is told which source files and other objects are needed to build each object, and is where object-specific compile settings are overridden.

To create a rule, first write the object name, followed by a colon and a space.  Then write the name of the object's source file :

```makefile
VATDEF.FILE: VATDEF.PF SAMREF.FILE
```

The example above is physical file `VATDEF.FILE`.  It is compiled from source code `VATDEF.PF` under the same directory of the `Rules.mk` file.

> [!WARNING]
>
> Note previous versions of TOBi required a `$(d)/` prefix on the source file, but this is no longer required and can be removed.  There also was an _object list_ section which broke down the list of target objects by type ( `TRGs` `DTAs` `SQLs` `BNDDs` `PFs` `LFs` `DSPFs` `PRTFs` `CMDs` `SQLs` `MODULEs` `SRVPGMs` `PGMs` `MENUs` `PNLGRPs` `QMQRYs` `WSCSTs` `MSGs`).  This is also unnecessary as of TOBi 2.4 since these are now automatically discovered.

If the object depends on other objects (referenced files or called programs) or source files (includes), add them to the end, separated by spaces:

`VATDEF.FILE` depends on physical file `SAMREF.FILE` which is defined somewhere else in the project.  Specifying dependencies is important, for this is what causes the physical file to automatically get recompiled when source code for its dependent physical file changes.

In summary, for the rules section, simply specify each object, followed by its source file (source-based objects) or primary object (non source-based objects),followed by any remaining dependencies.

---

> [!TIP]
>
> In order to determine if an object is out-of-date and needs to be built, TOBi looks within the library list (using VPATH for gmake gurus).  This library list consists of the current library list for your user profile that is updated via the iproj.json at the root of the project.  See [iproj.json documentation](iproj-json.md) for details.

---

#### Overriding compile settings

The generic TOBi makefile establishes what are hopefully sensible defaults for compile settings.  All of your projects will reference the same `def_rules.mk` file, so you can change its defaults to those shared among your projects (for example, TGTRLS is by default set to `V6R1M0`).

On the other hand, let's say you have an object that needs to be specially compiled at `V7R1M0`.  This directive is implemented by use of [target-specific variables](https://www.gnu.org/software/make/manual/make.html#Target_002dspecific), which is added as a separate line in the object's rule:

```makefile
JB110.MODULE: private TGTRLS := V7R1M0
JB110.MODULE: JB110.RPGLE
```

Above, module `JB110` will be compiled at a target release of `V7R1M0`.  The `private` modifier tells Make that the scope of the TGTRLS override is limited to `JB110.MODULE`.

The current list of overrideable compile attributes is:

- ACTGRP
- AUT
- BNDDIR
- COMMIT
- CURLIB
- DBGVIEW
- DETAIL
- DFTACTGRP
- DLTPCT
- HLPID
- HLPPNLGRP
- OBJTYPE
- OPTION
- PAGESIZE
- PGM
- PMTFILE
- PRDLIB
- REUSEDLT
- RPGPPOPT
- RSTDSP
- SIZE
- STGMDL
- SYSIFCOPT
- TERASPACE
- TEXT
- TYPE
- TGTCCSID
- TGTRLS
- USRPRF
- VLDCKR

#### Switches and options

TOBi's functionality and behavior can be adjusted by setting the values of certain options in the makefile.  Syntactically, setting an option is identical to overriding a compile attribute (as detailed above); the format is _`object_name: private option := value`_.

Following are the available makefile options.

##### CREATE_TYPEDEF

Setting `CREATE_TYPEDEF` to `YES` for a *FILE object (LF, PF, PRTF) results in a separate include-ready source file being generated that contains a typedef structure for the file object's record formats.  This feature is useful for C code that can no longer rely on `#pragma mapinc`, which doesn't work with IFS source code.  The generated file is named after the original source file, but with `.H` appended (source file `JB001.PF` results in include file `JB001.PF.H`)  Under the covers, the GENCSRC command is called.  Note that in the resulting struct, Bob changes `int` to `long int` to work with the SQL C compiler.

_Example:_

```text
# JB001.FILE -- CRTPF
JB001.FILE: private TEXT = Jumbo test file
JB001.FILE: private CREATE_TYPEDEF = YES
JB001.FILE: JB001.PF
```

#### Variables

If you have multiple targets with compile setttings to override, you can declare them as a variable with the syntax `MY_VAR := VAL`.

```text
PROJECT_TGTRLS := *PRV

PRO200.MODULE: private TGTRLS := $(PROJECT_TGTRLS)
PRO200.MODULE: PRO200.RPGLE

VAT.MODULE: private TGTRLS := $(PROJECT_TGTRLS)
VAT.MODULE: VAT.RPGLE
```

### Wildcarding

If you have multiple source that creates objects of the same type, you can make use of wildcarding.

#### Without Wildcarding

```text
FILE_TEXT := SAMPLE1
MOD_TEXT := SAMPLE2

```makefile
FILE_TGTRLS = V7R3M0
MOD_TGTRLS = V7R3M0

TEST1.FILE: private TGTRLS := $(FILE_TGTRLS)
TEST1.FILE: TEST1.TABLE DEP1.FILE DEP2.FILE

TEST2.FILE: private TGTRLS := $(FILE_TGTRLS)
TEST2.FILE: TEST2.TABLE DEP1.FILE DEP2.FILE

TEST1.MODULE: private TGTRLS := $(MOD_TGTRLS)
TEST1.MODULE: TEST1.RPGLE
```

#### With Wildcarding

```text
FILE_TEXT := SAMPLE1
MOD_TEXT := SAMPLE2

```makefile
FILE_TGTRLS = V7R3M0
MOD_TGTRLS = V7R3M0

%.FILE: private TGTRLS := $(FILE_TGTRLS)
%.MODULE: private TGTRLS := $(MOD_TGTRLS)

%.FILE: %.TABLE DEP1.FILE DEP2.FILE
%.MODULE: %.RPGLE
```

The above two examples are equivalent. Note the use of wildcards for overriding compile settings for objects of the same type.

The above two examples are equivalent. Note the use of wildcards for overriding compile settings for objects of the same type.

### Overriding with Wildcards

If you have objects you need to build which are outside the wildcard case, you can explicity set them, and this will take precedence over wildcarding.

```text
FILE_TEXT := SAMPLE1
MOD_TEXT := SAMPLE2

%.FILE: private TGTRLS := $(FILE_TGTRLS)
%.MODULE: private TGTRLS := $(MOD_TGTRLS)

%.FILE: %.TABLE DEP1 DEP2
%.MODULE: %.RPGLE

EMP.MODULE: private TGTRLS := V7R4M0
EMP.MODULE: EMP.RPGLE A.TABLE
```

## Further reading

To learn more about makefile syntax, see the official [GNU Make documentation](https://www.gnu.org/software/make/manual/make.html).  Just remember that every object referenced in a TOBi makefile must have an IFS file suffix (`.PGM`, `.FILE`, etc.) and be written in upper case.