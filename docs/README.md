<p align="center">
  <img alt="tobi" src="./assets/wordmark-logo.png">
</p>


<p align="center">
  A build system for native QSYS objects
</p>

<p align="center">
  <a href="https://github.com/IBM/ibmi-tobi/releases/latest"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/ibm/ibmi-tobi"></a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0"><img alt="GitHub" src="https://img.shields.io/github/license/ibm/ibmi-tobi"></a>
</p>

---

# The Object Builder for i (TOBi)

The Object Builder for i or _TOBi_ was known as Better Object Builder, or _Bob_ until 2025 when we hit a name collision with the very popular IBM Project Bob.  TOBi is a free and open source build system for the IBM i platform that is used to build native "QSYS" objects.  It was originally developed by [S4i Systems](http://www.s4isystems.com/), a leader in Electronic Document Management, to build their own software. In 2021, IBM began to make major investments in making TOBi span multiple directories and handle pseudo-source and a buildable project definition. TOBi is now hosted in IBM's public gihub and is under active development. It is released under the [Apache 2.0](https://github.com/IBM/ibmi-tobi/pull/LICENSE) license to the open source community so that others can contribute and benefit.

# Why Object Builder for i?

Here's what makes TOBi different.

* 🚀 **Speed.**  TOBi only compiles objects that need recompiling, like from new or changed source code.

* 🛠 **Reliability.**  TOBi understands the relationships between your objects, so if an item changes, then it and everything depending on it will be rebuilt.

* 💎 **Industry standard.**  Object dependencies are specified using standard makefile syntax, and the actual build engine is [GNU Make](https://www.gnu.org/software/make/) -- exactly like tens of thousands of Linux and Unix software projects.

* 🔧 **Flexibility.**  Most objects defined to TOBi typically build using your default values.  Have a program that requires a custom activation group or a data area that needs to be created with a certain value?  No problem, overriding compile parameters is trivial, and writing custom recipes for special objects is very straightforward.  If you can code it, you can build it.

* 🌟 **Ease of use.**  Invoking a build of an entire codebase is done with just a single command.  Or, if the Rational Developer for i integration pieces are installed, a single button click.

Learn more about installing and using TOBi in the [documentation](https://ibm.github.io/ibmi-tobi/).

