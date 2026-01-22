# Philosophy and Technical Overview
This page discusses, at a high level, what TOBi brings to the development process, what factors led to its development, and what the TOBi development model looks like.  Source control is a key player, so it is discussed, too.

## The classic IBM i development model
Historically, development on the IBM i looked a lot like this:  source code was stored in one or more source physical files in one or more libraries, edited in place with SEU or RDi, and manually compiled.  If a change management package was used, it handled the checking in and out of source code among a hierarchical set of libraries, ranging in purpose from development to QA to production.  Code was compiled manually on a per-object basis, unless a custom CL program was written to compile an entire project, or unless the change management software handled things.

When work began on a new version of the product, the existing source files would be duplicated to a new set of libraries.  Code fixes made to previous versions would often be manually copied to the newer versions.

It all worked, but it was sometimes a little cumbersome, good tools were often lacking, and the change management software could be expensive.

## What problems does TOBi solve?
These issues with the prior methodology were identified:
* Proprietary source control and build systems meant they were something of a black box.
* Bug fixes and new features were introduced on the vendor's timetable.
* Developing code usually required a persistent connection to the IBM i.
* Comparing code between product versions or development levels was difficult.
* Change management software/process questions sometimes required contacting Customer Support, often a slow process.
* Change management software was expensive.

The goal was to replace the proprietary source control and build system with something modern, open, industry-standard, and affordable.  It was decided to use Git for source control, GNU Make for building objects, and something like Trac or Jira for issue tracking.

## Git and the modern distributed development model
Git is the most popular version control system in use today.  It is open and free to use.  It differs from standard IBM i source control systems in that instead of having a single, centralized source code location, each developer has their own full-fledged repository.  Code can be worked on locally with the full protection of version control, and then changes can be shared with other developers.  It is also extremely flexible, feature-rich, and help is easily obtained due to the sheer quantity of developers using it.

_[What is Git](https://www.atlassian.com/git/tutorials/what-is-git)_ is an easily-absorbed introduction for those unfamiliar with it.

## Modern source control with IBM i code
To manage IBM i source code with Git, code needs to be taken out of source physical files and turned into standard text files, so that it becomes no different than source files from any other platform.  This unlocks a huge treasure trove of available PC/Linux tools, like code editors, source compare and merge tools, code review tools, etc.

Code _could_ be located in the IFS and edited with an IDE like RDi, but it is faster and more advantageous for developers to keep a local code repository on their PCs, edit the code locally (in RDi or equivalent), and push their changes to the i to be built.  Changes are also pushed to a centralized repository so that they are merged with changes from other developers.

## Building with Make
_Make_ is a popular build tool that builds objects from source code.  Key to the process is a _Makefile_, which is simply a text file that lists out how each item is built.  Make understands object dependencies, so if, for example, two programs use the same module, then Make will recompile the module and rebuild the two programs when the module's source code changes.

On the i, Make runs in PASE and knows nothing of ILE, RPG, modules, or service programs.  TOBi bridges the gap between the Linux/Unix environment with which Make is familiar and the QSYS file system in which most IBM i software lives.

## Putting it all together
Let's walk through a simple life cycle example.  A developer is asked to investigate a bug that manifested after a recent code change.  After making sure her local code repository contains the latest code, she gets to work.  She uses her Git client to see which lines of code have changed within the past several weeks, figures out the problem, and fixes the code.  She doesn't need to first check any code out, because her local repository is a complete mirror of the entire project.  Using TOBi, she pushes the changed code to her personal build directory on the development IBM i system, kicks off a build, tests the change, and sees that the issue is now resolved.  She merges her changes into the main codeline and syncs them with the central repository so her teammates benefit from her fixes.

## Presentation on historical motivation for TOBi
This PDF walks through the precursors to TOBi and their pros and cons and how we arrived at the current solution: <a href="https://github.com/IBM/ibmi-tobi/blob/master/docs/assets/BobOverview.pdf">Download PDF</a>