# User/Workspace Settings

> [!NOTE]
>
> Specifies the metadata for a user or a workspace. This part should be handled by the integrations.

Information for a project that will vary per deployment and so should not be hardcoded in the project.  

* Variables (can be used to name libraries for the object library or library list, or directories for the include path).  This allows the same project definition to target a different build library from one developer to another.  It would also allow TOBi to be used in CI/CD pipelines.  Before invoke a TOBi build, an environment variable should be set with the same name as the TOBi variable and with the desired value for that build.  So if the iproj.json said to use &objlib1 for the OBJLIB for compiles within a directory and the PASE command `export objlib1=PROJ_QA1` is run,  then the environment variable objlib1 would be set to “PROJ_QA” before invoking the build command.  Within the build shell script the value could be referenced via &objlib1.  Similarly the CI/CD mechanisms can set up  directories and object libraries using the exact same environment variable names.
* If you are developing on a different platforming and targeting an IBM i, you will need:
  * Hostname/ip address
  * Userid
  * (note that the password or private key is stored in a secure location depending on the development platform)
  * IFS build directory

* Tooling like Merlin/Code for IBM i/RDi might provide a UI to edit these values.