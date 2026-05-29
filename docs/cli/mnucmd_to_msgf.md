# mnucmd_to_msgf

## Synopsis

```
usage: mnucmd_to_msgf [-h] -f <srcstmf> -o <object> [-l <library>] [-c <cmd>] [-p [<parms>]]
                      [--save-joblog <path to joblog json file>] [--output <output>]
```

## Options

- **-f, --stream-file**

  Specifies the path name of the MNUCMD source file.

- **-o, --object**

  Enter the name of the message file object.

- **-l, --library**

  Enter the name of the library. If no library is specified, the created message file is stored in the current library.

  Default: `*CURLIB`

- **-c, --command**

  Command type used to create the message file.

  Default: `CRTMSGF`

- **-p, --parameters**

  Additional parameters for the message file creation. Currently used to extract the `TEXT('...')` description for the MSGF object.

- **--save-joblog**

  Output the joblog to the specified json file.

- **--output**

  Specifies the output log file path used by the build tooling.