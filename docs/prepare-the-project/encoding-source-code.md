# Encoding source in the IFS

### How the source in the IFS and git are encoded
We recommend that all source be encoded in UTF-8 or CCSID 1208.  This allows all characters to be represented in a single encoding which simplifies things tremendously.
If the source is copied from QSYS via CPYTOSTMF then be  sure to use the STMFCCSID parameter.  If you use TOBi's `cvttostmf` this encoding will automatically be chosen.
```cl
CPYTOSTMF ... STMFCCSID(1208)
```
But once you have migrated your source, your will be managing it via git and git clone will use the default CCSID of your IFS file system.  For V7R4 and V7R5, the environment variable PASE_DEFAULT_UTF8 allows you to make sure that any new source copied to the IFS via a PASE command like git will be in the right encoding.  For previous versions and with that setting turned off the encoding defaults to 819 which will not properly represent national characters.  
```
ADDENVVAR ENVVAR(PASE_DEFAULT_UTF8) VALUE(Y) LEVEL(*SYS)
```

### What EBCDIC encoding is used for literals during the compile
All of the IBM i compilers expect to read their source in EBCDIC. 
The value for this CCSID is derived from the [.ibmi.json](prepare-the-project/ibmi-json.md) `tgtCcsid` attribute.  This can be overridden at every directory level and if not overridden it derives its value from the parent directory.  If not specified at all it will be the `TGTCCSID(*JOB)` value where it takes the CCSID of the job.

### Language specific details
For further details that are specifc to each language see [this](prepare-the-project/compiler-specific.md).
