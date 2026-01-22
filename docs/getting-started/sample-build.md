# Build the sample project

Now that everything is installed and configured, let's build a [sample project](https://github.com/ibm/tobi-example).

## Perform a build

1. **Sign in to ssh**
   
   For instance:
   ```shell
   ssh ibmi01
   ```

1. **Create a library to build to.**

   ```cl
   system "CRTLIB LIB(TOBITEST) TEXT('The Object Builder for i test project')"
   ```
   
1. **Get the source from a sample git project**

   ```shell
   git clone https://github.com/ibm/tobi-example
   cd tobi-example
   ```

   If you didn't have git, simply do a `yum install git` to get it.

1. **Set an environment variable to point to the library you created**

   ```shell
   export lib1=TOBITEST
   ```

1. **Run the build using:**

   ```shell
   makei build
   ```

> [!TIP]
>
> Alternatively, you may combine the above two commands using makei's shortcut:<br>
> `makei b -e lib1=TOBITEST`

1. **You should see output similar to this.**

  ```
   $ makei b -e lib1=TOBITEST
   Set variable <lib1> to 'TOBITEST'
   > make -k BUILDVARSMKPATH="/tmp/tmpigspspcr" -k TOBI_PATH="/home/tongkun/git/ibmi-tobi" -f "/home/tongkun/git/ibmi-tobi/mk/Makefile" all
   === Creating RPG module [XML001.RPGLE]
   crtrpgmod module(TOBITEST/XML001) srcstmf('/home/tongkun/git/tobi-example/QRPGLESRC/XML001.RPGLE') AUT() DBGVIEW(*ALL) OPTION(*EVENTF) OUTPUT(*PRINT) TEXT('') TGTCCSID(297) TGTRLS()
   ✓ XML001.MODULE was created successfully!
   ...
   ...
   Objects:             13 failed 97 succeed 110 total
   └ Failed objects:    ART301.MODULE FARTICLE.SRVPGM ART200D.FILE ORD100D.FILE ORD101D.FILE ART200.PGM ART201.PGM ART202.PGM ORD100.PGM ORD700.PGM ARTLSTDAT.FILE CUSSEQ.DTAARA ORDERCUS.FILE
   Build Completed!
  ```

  * all of the output is stored in `.logs/output.log`
  * all of the job logs are gathered in '.logs/joblog.json` and can be viewed with any JSON viewer
  * the event files for all compiles are gathered under the `.evfevent` directory

## The sample build process in action (quadruple speed)

<!-- ![Sample Build Demo](sample-build.assets/sample-build.gif) -->


> [!TIP]
> A few other options can be used:<br>
>   `makei c -f functionsVAT/VAT300.RPGLE` to compile the `VAT300.RPGLE` into `VAT300.MODULE`<br>
>   `makei b -d functionsVAT` to build the `functionsVAT` subdirectory<br>
>   Check out the [usage of makei](cli/makei.md)
