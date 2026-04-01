# crtfrmstmf

## Synopsis

```
usage: crtfrmstmf [-h] -f <srcstmf> -o <object> [-l <library>] -c <cmd> [-p [<parms>]] [--ccsid [<ccsid>]]
                  [--save-joblog <path to joblog json file>]
```

## Options

- **-f, --stream-file**

  Specifies the path name of the stream file containing the source code to be compiled.

- **-o, --object**

  Enter the name of the object.

- **-l, --library**

  Enter the name of the library. If no library is specified, the created object is stored in the current library.

  Default: `*CURLIB`

- **-c, --command**

  Possible choices: `CRTCMD`, `CRTBNDCL`, `CRTCLMOD`, `CRTDSPF`, `CRTPRTF`, `CRTLF`, `CRTPF`, `CRTMNU`, `CRTPNLGRP`, `CRTQMQRY`, `CRTSRVPGM`, `CRTWSCST`, `CRTRPGPGM`, `CRTSQLRPG`

  Specifies the compile command used to create the object.

- **-p, --parameters**

  Specifies the parameters added to the compile command.

- **--ccsid**

  The CCSID used to create the SRC-PF in QTEMP


- **--save-joblog**

  Output the joblog to the specified json file.
