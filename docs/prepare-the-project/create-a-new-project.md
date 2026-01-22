# Create a new project

## Interactive Setup

We have provided an interactive initializing program inside `makei` which walk you through a list of options and sets up the project for you. To create a project, run:

```bash
makei init
```

At the end you will see:

```diff
-bash-5.1$ makei init
This utility will walk you through creating a project.
It only covers some common items.

Press ^C at any time to quit.
descriptive application name: (yourName)
git repository: http://github.com/youruser/yourName
include path, separated by commas:
What library should objects be compiled into (objlib): (*CURLIB) &pgmlib
What EBCDIC CCSID should the source be compiled in: (*JOB)
curlib: (*CRTDFT) &pgmlib
Pre user libraries, separated by commas:
Post user libraries, separated by commas:
Set up commands to be executed, separated by commas:
license:

The following files will be added to the project
+ /home/REINHARD/git/yourName/iproj.json
+ /home/REINHARD/git/yourName/Rules.mk
Continue? (yes)
```

Simply press enter to confirm the changes and you have created a minimal TOBi project.

## Manually Setup

You may choose to manually setup the project by creating

- [x] `iproj.json` at the project root
- [x] `.ibmi.json` at the directories you want to override build variables to target a different object library, or use a different EBCDIC CCSID for the compile.
- [x] `Rules.mk` at each level of the project defining the targets

So far, we have created:

- [project level metadata iproj.json](prepare-the-project/iproj-json)
- [directory level metadata .ibmi.json](prepare-the-project/ibmi-json)

- [Rules.mk](prepare-the-project/rules.mk.md) defining the directory level targets to build
