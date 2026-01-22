# Installing IBM i Prerequisites

Some software needs to be installed on the IBM i before TOBi can be used to compile software.


## Install PASE

The build system uses Unix and GNU tools, which run inside of PASE, so PASE must be installed if it already isn't.

[Installing IBM PASE for i](https://www.ibm.com/docs/en/i/7.4?topic=i-installing-pase)

> To install PASE for i on your system, follow these steps:
>
> 1. On an IBM i command line, enter `GO LICPGM`.
> 2. Select `11 (Install licensed program)`.
> 3. Select Option `33 (5770-SS1 - Portable Application Solutions Environment)`.
> 4. Optional: Install additional locales.

## Install IBM i Open Source Technologies

IBM provides many open source technologies ported to work on IBM i. TOBi depends on a few of them, namely bash, make-gnu, python3, gawk, grep-gnu, sed-gnu, coreutils-gnu, python3-ibm_db.

One of the easier ways to manage the open-source tools is through ACS. Here are some instructions on [how to install and manage the open-source packages](https://www.ibm.com/support/pages/getting-started-open-source-package-management-ibm-i-acs)

You can then use the ACS GUI or the command line to install packages.

### Install Bash

The default shell on the IBM i is the Bourne shell (_see:_ [_IBM PASE for i shells and utilities V7R4_](https://www.ibm.com/support/knowledgecenter/en/ssw_ibm_i_74/rzalf/rzalfpase.htm)). We recommend changing this to the [*Bash*](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) shell because *Bash* is more user-friendly and feature-rich.  

```bash
yum install bash
```



### Configure the .bash_profile

> [!NOTE]
> Since we assume bash is used in this documentation, we use **.bash_profile** instead of [*Environment Setup Using /QOpenSys/etc/profile and $HOME/.profile*](https://www.ibm.com/support/pages/portable-application-solutions-environment-pase-envrionment-setup-using-qopensysetcprofile-and-homeprofile)

It is important that the directory `/QOpenSys/pkgs/bin` directory is on your path.

You can add the following lines to the `$HOME/.bash_profile` file (or create it if it does not exist).

```bash
# Set the path to find IBM open-source ports as well as Perzl AIX binaries
export PATH="/QOpenSys/pkgs/bin:${PATH}"
```



### Make Bash the default shell

Changing shells on IBM i is described [here](https://ibmi-oss-docs.readthedocs.io/en/latest/troubleshooting/SETTING_BASH.html).
To do this, run the following command. The first line is only necessary if *chsh* is not already installed.

```bash
yum install chsh
chsh -s /QOpenSys/pkgs/bin/bash
```

alternatively, you can use SQL

```sql
CALL QSYS2.SET_PASE_SHELL_INFO('*CURRENT', '/QOpenSys/pkgs/bin/bash')
```




> [!WARNING]
> If you did not add `/QOpenSys/pkgs/bin` to the PATH variable, you may not be able to invok *yum* or *chsh* directly. Try specifying the full path using `/QOpenSys/pkgs/bin/yum` or `/QOpenSys/pkgs/bin/chsh`.

## TGTCCSID support on the ILE RPG and COBOL compilers

TOBi supports specifying the EBCDIC CCSID to compile the source in. This requires the TGTCCSID parameter on the RPG and COBOL compiler commands. Details of which PTFs are needed on which release are found [here](prepare-the-project/compiler-specific.md).

## Ensure the SSH daemon is running

Here is some good [background](https://www.seidengroup.com/2020/11/16/getting-started-with-ssh-for-ibm-i/) on ensuring SSH is available on IBM i and why.
Typically the [5733-SC1 Licensed Program Product](https://www.ibm.com/support/pages/node/1128123/) is already installed as part of the operating system.

To start the server:

```cl
STRTCPSVR SERVER(*SSHD)
```

## Use an internet time server to keep timestamps in sync

TOBi uses gmake, which compares the timestamps of source and their compiled objects to determine exactly what needs to get compiled. If you are synchronizing your source to IFS from your IDE or PC workspace, it is important that they agree on what time it is. The following commands can be used to set up the NTP server to synchronize clocks to an internet server.

```cl
CHGNTPA RMTSYS('0.us.pool.ntp.org') POLLITV(1)
STRTCPSVR SERVER(*NTP) NTPSRV(*CLIENT)
```
The first command says to synchronize with a specific server. You can find a local server here https://www.ntppool.org/zone/@ if you don't have one in your shop.



Installation of IBM i prerequisites is now complete. :smile:

