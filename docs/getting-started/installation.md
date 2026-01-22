# Installation
> [!WARNING]
> Some software needs to be installed on the IBM i before TOBi can be installed.
> Please follow the [instructions to install prerequisites](getting-started/prerequisites.md) before continuing here.


## **Install via yum package manager**

***YUM*** is a package management utility for RPM-based distributions. We recommend using *yum* to install *tobi* and its dependencies.

> [!TIP]
> Make sure you have installed the IBM i package repositories `ibmi-repos`.
>
> If not, run `yum install ibmi-repos` before installing `tobi`.
> if `ibmi-repos` is present but the `tobi` package is not found in it then do the following in order to update the repository.
> ```bash
> yum upgrade yum ibmi-repos
> yum upgrade ibmi-repos
> ```
> if that does not work clean up the metadata with
> ```bash
> yum clean metadata
> ```

```bash
 # Install tobi
yum install tobi
```

If you have installed `bob` previously, you will have to uninstall 
it before installing `tobi` which is the latest version.  To do so, 
simply do 
```bash
yum erase bob
```

## Verify TOBi is installed correctly

You may check if TOBi is installed correctly by invoking `makei` on IBM i. You should see an output similar to this.

```
$ makei
usage: makei [-h] [-v] command ...

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  print version information and exit

These are common makei commands:
  command
    init         set up a new or existing project
    info         get information about the current project
    compile (c)  compile a single file
    build (b)    build the whole project
    cvtsrcpf     convert source physical file members to ASCII IFS files
```

If you see something like `makei: A file or directory in the path name does not exist.` Ensure that there is no error in the installation step and that you have [setup the environment](getting-started/prerequisites?id=configure-the-bash_profile) correctly.

If you still have issues, [submit an issue](https://github.com/IBM/ibmi-tobi/issues/new).
