## Changes in Bob v2

Bob v2 now known as The Object Builder for i (TOBi) ([IBM/ibmi-tobi](https://github.com/IBM/ibmi-tobi)) improves many aspects over original Bob developed by S4i ([s4isystems/Bob](https://github.com/s4isystems/Bob)).

If you previously used Bob v1, the following changes should be noted.

***

## Dependencies

Since Bob v2, we require additional packages to be installed on the IBM i as the following:

[More on the Prerequisites for IBM i](getting-started/prerequisites.md) 

## Installation

In Bob v1, we install `Bob` by putting all the `Bob` files under `/Build/Bob` and point to it in the makefiles we create for the project.

In TOBi we provide the `RPM` package to specify the dependencies and install `Tobi` into the system path automatically.

Since Bob v2.3.5, you may install Bob/Tobi using the `yum` package manager

[More on the install instructions](getting-started/installation.md)

## Project Structure

In Bob V1, every directory is treated as a project and we need to create the `Makefile` for every directory.

Since Bob v2, we don't create the `Makefile` anymore and we can define a project with multiple directories and specify the dependencies around them. Now the project is defined using the new metadata files.

### Metadata Files

- `iproj.json`: we will define a project using `iproj.json`, `Tobi` will treat the directory containing this file as the root of the project. [More on the Project Level iproj.json](prepare-the-project/iproj-json.md) 

- `Rules.mk`: in this file, we specifies the structure of the project (i.e. subdirectories) and the object to be created as well as their dependencies. `Bob` will load those files dynamically and create a single `Makefile` for the `make` program to deal with the dependency relations. [More on creating Rule.mk](prepare-the-project/rules.mk.md) 

- `.ibmi.json`: in this file, we allow developer to override configurations such as target CCSID and object library for the containing directory and its subdirectories.  [More on the directory level metadata .ibmi.json](prepare-the-project/ibmi-json.md) 

A sample project for Bob v2 can be found at [edmundreinhardt/tobi-example](https://github.com/edmundreinhardt/tobi-example).

### Logs

In Bob v1, after running a build, we get all the compiler output in `stdout` or in the `makelog.log` file if run from the `makelog` script and we have the event files in the `.evfevent` directory.

In Bob v2, we have the following logs:

- all the make output goes to the `stdout`

- all of the compiler output is stored in `.logs/output.log`
- all of the job logs are gathered in `.logs/joblog.json` and can be viewed with any JSON viewer
- the event files for all compiles are gathered under the `.evfevent` directory



## Bob Changes

In Bob v1, we define all the build rules in the `IBMiMakefile`.



## Client Tools

In Bob v1, we use the build settings file `.buildsettings` to setup the client tools including the user/project metadata.

## CLI Updates

In Bob v2, we provide a new CLI tool `makei` to interact with Bob.

## Single File Compile

Since Bob v2, we support compiling a single file using `makei compile -f {filename}`.

## Building the contents of single directory

Since Bob v2, we support building everything within a directory using  `makei build -d {directoryname}`.

## New Object Types

The following object types are supported as pseudo-source.  
The CL command to create the object is stored in a file with the given extension.  

| Object Type | File Extension | CL Command        |
| :---------- | :------------- | :---------------- |
| *MSGF       | .MSGF          | CRTMSGF + ADDMSGD |
| *BNDDIR     | .BNDDIR        | CRTBNDDIR         |
| *SRVPGM     | .ILESRVPGM     | CRTSRVPGM         |

## Support SQL pseudo-source

The following SQL types are supported as pseudo-source.  
The set of SQL commands to create the object is stored in a file
with the given extension.  Typically it is just the CREATE OR REPLACE command, but for example 
for TABLE, you would also want to include any ALTER TABLE commands as well.  Other ancillary 
commands needed to complete creation like LABEL ON should also be in the same source file. 

| SQL Type  | QSYS Object | File Extension | SQL COMMAND                 |
| :-------- | :---------- | :------------- | :-------------------------- |
| TABLE     | *FILE       | .TABLE         | CREATE OR REPLACE TABLE     |
| VIEW      | *FILE       | .VIEW          | CREATE OR REPLACE VIEW      |
| PROCEDURE | *PGM        | .SQLPRC        | CREATE OR REPLACE PROCEDURE |
| FUNCTION  | *SRVPGM     | .SQLUDF        | CREATE OR REPLACE FUNCTION  |
| FUNCTION  | *SRVPGM     | .SQLUDT        | CREATE OR REPLACE FUNCTION  |
| TRIGGER   | *PGM        | .SQLTRG        | CREATE OR REPLACE TRIGGER   |
| ALIAS     | *FILE       | .SQLALIAS      | CREATE OR REPLACE ALIAS     |
| SEQUENCE  | *DTAARA     | .SQLSEQ        | CREATE OR REPLACE SEQUENCE  |