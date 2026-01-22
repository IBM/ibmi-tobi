# Frequently Asked Questions

Below you'll find answers to the most commonly asked questions.
If you don't find the answer you are looking for.
Check out the [support](Support.md) page and [submit an issue](https://github.com/IBM/ibmi-tobi/issues).

+ I just extracted my source from source control and I am pointing to a library with object that are already built.  I only want to rebuild objects from source that I change after the extract? +

  TOBI is based on gmake so it is timestamp-driven.  The simplest solution is to simply touch all of the files just extracted so that they are older than the objects they will compile into.  Then only files that are edited will trigger builds.

  ```bash
  find DIRECTORY -exec touch -d "2 days ago" {} +
  ```
  Where DIRECTORY is the IFS directory containing your source.
  If you know the oldest object, which you can find via 'ls -ltr /QSYS.LIB/MYLIB.LIB' etc.
  You could then do:

  ```bash
  find DIRECTORY -exec touch -d "$(date -R -r /QSYS.LIB/MYLIB.LIB/OLDESTOBJ.PGM)" {} +
  ```
  so for example
  ```bash
  -bash-5.1$ ls -ltr /QSYS.LIB/TOBIBUILD1.LIB | head -n 2
  total 11920
  drwx---rwx 2 reinhard 0  20480 Oct  8 17:35 SAMREF.FILE
  ```
  and then I go to my source directory and run
  ```bash
  -bash-5.1$ find . -exec touch -d "$(date -R -r /QSYS.LIB/TOBIBUILD1.LIB/SAMREF.FILE)" {} +
  -bash-5.1$ ls -l
  total 40
  -rwx------ 1 reinhard labusers  178 Oct  8 17:35 FVAT.BND
  -rwx------ 1 reinhard labusers  230 Oct  8 17:35 Rules.mk
  -rwx------ 1 reinhard labusers 1118 Oct  8 17:35 VAT.RPGLEINC
  -rwx------ 1 reinhard labusers 2170 Oct  8 17:35 VAT300.RPGLE
  -rwx------ 1 reinhard labusers  689 Oct  8 17:35 VATDEF.PF
  ```
  Or to combine it into a single command
  ```bash
find . -exec touch -d "$(date -R -r /QSYS.LIB/TOBIBUILD1.LIB/$(ls -tr /QSYS.LIB/TOBIBUILD1.LIB | head -n 1))" {} +
  ```