## **Install a prebuilt RPM packages**

1. TOBi depends on many open source packages. You need to install the dependencies first before continuing.

```bash
yum install bash coreutils gawk grep-gnu make-gnu python39 python39-ibm_db sed-gnu
```

2. You may always grab the latest binary from the [releases](https://github.com/ibm/ibmi-tobi/releases) page.

To download the latest rpm file on IBM i, run the following

```bash
curl -L https://github.com/IBM/ibmi-tobi/releases/latest/download/tobi.rpm -o tobi.ppc64.rpm
```


* If you want to test an older release, you can grab the URL from the [latest release on GitHub](https://github.com/ibm/ibmi-tobi/releases).
    * right click on the `.rpm` file and copy the link URL.

3. Install the `.rpm`

```bash
# install TOBi from rpm file
rpm -i tobi.ppc64.rpm
```
or upgrade from a previous version
```bash
# upgrade TOBi from rpm file
rpm -U tobi.ppc64.rpm
```


## Verify TOBi is installed correctly

You may check if tobi is installed correctly by invoking `makei` on IBM i. You should see an output similar to this.

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
