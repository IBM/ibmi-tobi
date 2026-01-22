# makei

## Synopsis

```bash
usage: makei [-h] [-v] command ...
```

## Options

- **-v, --version**

  print version information and exit

## These are common makei commands

- **command**

  Possible choices: init, compile, c, build, b, cvtsrcpf

## Sub-commands:

### init

?> set up a new or existing project

```
makei init [-h] [-f]
```

#### Options

- -f, --force

  force overwrite any existing files

---

### compile (c)

?> compile a single file

```
makei compile [-h] (-f <filename> | --files <filepaths>) [-o <options>]
              [-e <var>=<value>] [--tobi-path <path>]
```

#### Options

- **-f, --file**

  file to compile

- **--files**

  files and/or directories to compile, separated by colon (:)

- **-o, --make-options**

  options to pass to make

- **-e, --env**

  override environment variables

- **--tobi-path**

  path to the TOBi directory

- **-l, --log**

  log tracing information to .trace-makei to diagnose why things are not working as expected

---

### build (b)

?> build the whole project

```
makei build [-h] [-t <target> | -d <subdir>] [-o <options>] [--tobi-path <path>]
            [-e <var>=<value>]
```

#### Options

- **-t, --target**

  target to be built

- **-d, --subdir**

  subdirectory to be built (identical to __makei compile -f__)

- **-o, --make-options**

  options to pass to make

- **--tobi-path**

  path to the directory where TOBi is installed

- **-e, --env**

  override environment variables
  
- **-l, --log**

  log tracing information to .trace-makei to diagnose why things are not working as expected

  ---

### cvtsrcpf

?> convert source physical file members to ASCII IFS files


```
makei cvtsrcpf [-h] [-c <ccsid>] [-l] [-t] <file> <library>
```

Converts all members in a source physical file to properly-named (TOBi-compatible), UTF-8 encoded, LF-terminated source files in the current directory in the IFS. Generally speaking, the source member type will become the filename extension.

For example, RPGLE source member `AB1001` will become IFS source file `AB1001.RPGLE`. Four exceptions exist, however: source member types CMD, MENU, and PNLGRP result in filename extensions .CMDSRC, .MENUSRC, and .PNLGRPSRC, respectively, and source member type C residing in source physical file H results in filename extension .H.

All source files will be encoded in UTF-8. If the source physical file was created successfully, a `.ibmi.json` file with the CCSID value from the SRC-PF will be created in the same directory. Note that it will not override an existing `.ibmi.json` file. [Link to discussions](https://github.com/IBM/ibmi-tobi/pull/115#issuecomment-1194661949)

If the SRC-PF is 65535, then the value of the `ccsid` parameter of the cvtsrcpf command will be used.

If the parameter is not specified the `*JOB` CCSID should be used.

It is likely that the same destination directory will contain converted members from many source physical files.  Therefore, name collisions are possible.  In the event of a duplicate member name and type, the source file name will be adjusted from `member.type` to `member (n).type`, with `n` incremented until a unique name is achieved.
 

#### Arguments

- **file**

  the name of the source file

- **library**

  the name of the library

#### Options

- **-c, --ccsid**

  An optional CCSID to use as `TGTCCSID` on compiles if the SRC-PF CCSID being migrated is 65535. See above for in-depth description.

- **-l, --tolower**

  The generated source file name will be in lowercase.

- **-t, --text**

  The generated source file will include the member text as a comment. Note that besides the EBCDIC CCSID, the member text is the only other piece of metadata associated with a SRC-PF member outside of its contents. Build tools like TOBi and Arcad Builder know how to extract this text description and specify it on the appropriate compile command so that the resultant object has the same description.

#### Example

- Convert source members for file MYLIB/MYSRCFILE into directory `newdir` using the default (UTF-8).'
  ```bash
  cd newdir
  makei cvtsrcpf mysrcfile mylib
  ```

- Convert source members for file MYLIB/MYSRCFILE into directory `newdir` using Windows Latin-1.
  ```bash
  cd newdir
  makei cvtsrcpf -c 1252 mysrcfile mylib
  ```