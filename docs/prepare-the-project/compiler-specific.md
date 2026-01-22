# Compiler Specific Requirements

## How source is compiled from the IFS

| Language    | Compile from IFS                | Specify EBCDIC encoding |
| :---------- | :------------------------------ | :---------------------- |
| ILE C/CPP   | SRCSTMF() <sup>[1](#fn1)</sup> | TGTCCSID() <sup>[2](#fn2)</sup> |
| ILE RPG     | SRCSTMF() <sup id="a1">[1](#fn1)</sup> | TGTCCSID() <sup id="a3">[3](#fn3)</sup> |
| ILE COBOL   | SRCSTMF() <sup>[1](#fn1)</sup> | TGTCCSID() <sup id="a4">[4](#fn4)</sup> |
| ILE CL      | limited to CRTFRMSTMF <sup id="a6">[6](#fn6)</sup> | CRTFRMSTMF -ccsid <sup id="a5">[5](#fn5)</sup> |
| SQL         | RUNSQLSTM SRCSTMF() | UTF8 is supported |
| CMD         | SRCSTMF() <sup>[1](#fn1)</sup> | job must have compatible CCSID <sup id="a7">[7](#fn7) |
| OPM, DDS, PNLGRP, MENU, CMD   | CRTFRMSTMF <sup>[5](#fn5)</sup> | CRTFRMSTMF -ccsid <sup>[5](#fn5)</sup> |

The value for the EBCDIC CCSID used to compile is derived from the [.ibmi.json](prepare-the-project/ibmi-json.md) `tgtCcsid` attribute.  This can be overridden at every directory level and if not overridden it derives its value from the parent directory.  If not specified at all it will be the `TGTCCSID(*JOB)` value where it takes the CCSID of the job.

<b id="fn1">1</b>: Modern ILE compilers support the `SRCSTMF(ifs/path)` parameter to compile directly from the 
IFS file system.  There are not issues with line length etc.[↩](#a1)

<b id="fn2">2</b>: Modern compilers support the `TGTCCSID(ebcdic-ccsid)` parameter to specify the CCSID that the UTF-8 IFS source should be transformed to before compiling.  This allows national characters in string literals etc. to be preserved. [↩](#a2)


<b id="fn3">3</b>: The ILE RPG TGTCCSID() parameter was added in V7R4. For IBM i 7.3 please make sure the PTF `SI74590` in product `5770WDS` is applied.  Otherwise the compile will fail because the TGTCCSID parameter will not be recognized.  TOBi is not supported on IBM i 7.2 and earlier.
[↩](#a3)

<b id="fn4">4</b>: The ILE COBOL TGTCCSID() parameter was added in V7R5.  You may have to install PTFs to get this support. 

7.3:
- The ILE COBOL command processing program for CRTBNDCBL and CRTCBLMOD: `5770WDS SI81472`
- ILE COBOL compiler: `5770WDS SI81475`
- ILE COBOL commands CRTBNDCBL and CRTCBLMOD: `5770WDS SI81473`

7.4: TR8 or
- The ILE COBOL command processing program for CRTBNDCBL and CRTCBLMOD: `5770WDS SI81006`
- ILE COBOL compiler: `5770WDS SI81553`
- ILE COBOL commands CRTBNDCBL and CRTCBLMOD: `5770WDS SI81023`

7.5: TR2 or 
- The ILE COBOL command processing program for CRTBNDCBL and CRTCBLMOD: `5770WDS SI81047`
- ILE COBOL compiler: `5770WDS SI81048`
- ILE COBOL commands CRTBNDCBL and CRTCBLMOD: `5770WDS SI81049`

Otherwise the compile will fail because the TGTCCSID parameter will not be recognized.[↩](#a4)

<b id="fn5">5</b>:  The `crtfrmstmf` command copies the stream file to a source member in SRC-PF create in QTEMP.  The `-ccsid` parameter specifies the encoding for that SRC-PF.  However it is important that the job running the compile is able to read that encoding without losing any characters.  Note that this is no different than compiling from a QSYS member.
[↩](#a5)

<b name="fn6">6</b> CL has the `SRCSTMF` parameter but not the `TGTCCSID` parameter.  In order to support national characters in CL, TOBi has elected to use the `crtfrmstmf` support.
[↩](#a6)

<b name="fn7">7</b> The CRTCMD command does not yet support the `TGTCCSID` parameter.  To avoid encoding problems, ensure that the CCSID of the job invoke TOBi has a compatible CCSID.
[↩](#a7)
