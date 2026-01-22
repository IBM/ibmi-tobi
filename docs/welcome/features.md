# The Object Builder features

Some of the major benefits of using a The Object Builder / Git / RDi development environment are:

* Consistent, repeatable software builds
* At-a-glance version history
* Easily examine code from any point in time
* Easily compare code changes between any two points in time
* Flexible source code version control to fit any development workflow
* Git and Make are ubiquitous; volumes of documentation and help exist
* Automated builds are possible
* Speedy delta builds -- only new and changed code (and code dependent on the changed code) is compiled
* Fast transfer of source files from PC to IBM i
* One-button builds
* Open source.  Free to use and free to modify.

Obviously, we think TOBi is pretty great.  But, in fairness, there are some challenges to be aware of:

* Learning curve -- Git and Make are amazing but can also be quite complex.  Fortunately, the vast wealth of online information will help you recover from any mistake.
* Installation -- Installing the IBM i prerequisites used to be daunting but has been reduced to a single rpm command
* PASE -- Since Git (if installed on the IBM i) and Make run in PASE, some familiarity with a Unix-like shell is helpful.  It may be a little outside your comfort zone, but it is a tremendous skill to have.  We have performed search-and-replace instructions on thousands of source files using Sed and regular expressions in mere seconds, and used Grep to almost instantly discover every source file using a specific physical file.
* At its current stage in development, changes to service programs and files result in rebuilds of everything using them.  This is to avoid signature violations and level checks.  This will be addressed in a future version of TOBi.

## Supported object types

These IBM i source types can be compiled directly from the IFS

| Object Type | File Extension                                                        |
| :---------- | :-------------------------------------------------------------------- |
| *CMD        | .CMD                                                                  |
| *MODULE     | .RPGLE, .CLLE, .C, .SQLC, .CPP, .SQLCPP, .SQLRPGLE, .CBLLE, .SQLCBLLE |
| *PGM        | .PGM.RPGLE, .PGM.SQLRPGLE, .PGM.C, .PGM.CBLLE, .PGM.SQLCBLLE, .RPGLE, .SQLRPGLE          |
| *SRVPGM     | .BND                                                                  |

Note:

* to make it unambiguous whether a source file is to be compiled into a PGM or MODULE, the PGM source has .PGM.<srctype> as its file extension
  * Support now exists to build a PGM directly from a RPGLE or SQLRPGLE source file.
  The decision to build a MODULE or a PGM will be specified in Rules.mk 
  * Eg: CUSTOMER.PGM.RPGLE and CUSTOMER.RPGLE can create a PGM
* it is very easy to build SRVPGM using binder source.  Simply have a rule like
  * CUSTOMER.SRVPGM: $(d)/CUSTOMER.BND A.MODULE B.MODULE


These older IBM i source types are compiled directly from the IFS using the CRTFRMSTMF open source project that copies the source to QTEMP/QSOURCE before compiling and then fixes the EVENTF members to point to the original IFS source

| Object Type | File Extension                      |
| :---------- | :---------------------------------- |
| *FILE       | .DSPF, .LF, .PF, .PRTF              |
| *MENU       | .MENUSRC                            |
| *MODULE     | .CLLE                               |
| *PGM        | .RPG, .PGM.CLLE                     |
| *PNLGRP     | .PNLGRPSRC                          |
| *WSCST      | .WSCSTSRC                           |
| *QMQRY      | .SQL                                |

Note:

* OPM COBOL .CBL cannot be supported because the OPM COBOL compiler calls RCLRSC which cannot be run from PASE

## Support CL pseudo-source

The following object types are supported as pseudo-source.  
The CL command to create the object is stored in a file with the given extension.  

Note that for *MSGF and *BNDDIR, the CL commands should include the delete of the MSGF and BNDDIR before creating the new one in order to avoid the timestamp getting old and breaking the make processing.

Normal processing of commands will continue until an error is reached unless prefixed with a `!` in front of the command. 

Usage the prefix of `!` will ignore any errors for the command. 
ex. `!DLTBNDDIR XXXX/YYYYY` will then ignore the error if the Binding Directory does not exist and continue processing. 


| Object Type | File Extension | CL Command        |
| :---------- | :------------- | :---------------- |
| *MSGF       | .MSGF          | CRTMSGF + ADDMSGD |
| *BNDDIR     | .BNDDIR        | CRTBNDDIR         |
| *PGM        | .ILEPGM        | CRTPGM            |
| *SRVPGM     | .ILESRVPGM     | CRTSRVPGM         |
| *DTAARA     | .DTAARA        | CRTDTAARA         |
| *DTAQ       | .DTAQ          | CRTDTAQ           |
| *TRG        | .SYSTRG        | ADDPFTRG          |

Note:

* this provides a second way of creating programs and service programs using the .ILEPGM and .ILESRVPGM file types.  This gives a high degree of customization in that you can specify any and all parameters on the command and even additional commands.  But it is more work than the simple dependency line needed when building from binder source.

### Placeholders in Pseudo Source Files (&O and &N)

* **&O (Object Library Placeholder)**:
This placeholder is used to represent the library where an object resides.

Example Usage: If a command in a pseudo source file is CRTPGM PGM(&O/MYPGM), and the script is invoked with MYLIB as the object library, the command executed will become CRTPGM PGM(MYLIB/MYPGM).

* **&N (Object Name Placeholder)**:
This placeholder is used to represent the name of the object.

Example Usage: If a command in a pseudo source file is DSPPGM PGM(&O/&N), and the script is invoked with MYLIB as the object library and MYPGM as the object name, the command executed will become DSPPGM PGM(MYLIB/MYPGM).

## Support SQL pseudo-source

The following SQL types are supported as pseudo-source.
The set of SQL commands to create the object is stored in a file with the given extension. Typically it is just the CREATE OR REPLACE command, but for example for TABLE, you would also want to include any ALTER TABLE commands as well.  Other ancillary commands needed to complete creation like LABEL ON should also be in the same source file. 

| SQL Type  | QSYS Object | File Extension  | SQL COMMAND                 |
| :-------- | :---------- | :-------------- | :-------------------------- |
| TABLE     | *FILE       | .TABLE or .PFSQL| CREATE OR REPLACE TABLE     |
| VIEW      | *FILE       | .VIEW           | CREATE OR REPLACE VIEW      |
| INDEX     | *FILE       | .INDEX          | CREATE INDEX                |
| PROCEDURE | *PGM        | .SQLPRC         | CREATE OR REPLACE PROCEDURE |
| FUNCTION  | *SRVPGM     | .SQLUDF         | CREATE OR REPLACE FUNCTION  |
| FUNCTION  | *SRVPGM     | .SQLUDT         | CREATE DISTINCT TYPE        |
| TRIGGER   | *PGM        | .SQLTRG         | CREATE OR REPLACE TRIGGER   |
| ALIAS     | *FILE       | .SQLALIAS       | CREATE OR REPLACE ALIAS     |
| SEQUENCE  | *DTAARA     | .SQLSEQ         | CREATE OR REPLACE SEQUENCE  |
| VARIABLE  | *SRVPGM     | .SQLVAR         | CREATE OR REPLACE VARIABLE  |

Generic SQL statements with file extension .SQL are executed using RUNSQLSTM

### Incremental SQL pseudo-source

If you want different source to run if your object is already built, but want to maintain your code in the same file, write that SQL pseudo-source in the incremental block. Only if the object exists in your library list, will the incremental pseudo-source run. Otherwise, source outside of the block will be the one which runs.

```
incremental {
 ALTER TABLE ADD COLUMN ...
}

CREATE OR REPLACE TABLE ...
```