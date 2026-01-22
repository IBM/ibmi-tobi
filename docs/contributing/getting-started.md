# Getting Started
We are glad you are interested in contributing to TOBi. This document will help you get started.

## Get the source code

To work on TOBi, you need to get the source code. You can do this by cloning the repository:

```bash
git clone git@github.com:IBM/ibmi-tobi.git
cd ibmi-tobi
```

## Set up the develop environment
For developing TOBi, you should install `Python3` and `nox` on your computer.

To install nox. Often, you can run the following to install and use it.
```base
python -m pip install nox
```

We recommend you to use `virtualenv` to create a virtual environment for TOBi development.
We've configured `nox` to set up the virtual environment for you. You can run the following
command to create a virtual environment and install all the dependencies.
```bash
nox -s dev
```

## Run the tests
To run the tests, you can run the following command:
```bash
nox -s test
```

## Run the linter
To run the linter, you can run the following command:
```bash
nox -s lint
```

## Release process
1. Once all the tests and linters pass, you can create a pull request to the `master` branch.
2. Switch to the `master` branch and pull the latest code.
3. Update the CHANGELOG file under the `changelogs` folder. Make sure that on the first line
the date and version are correct!  Commit this change.
4. Use `nox -s release -- {major, minor, patch}` to release a new version. For example, 
if you want to release a new patch version, you can run `nox -s release -- patch`. This will bump
the version number, create a new tag, and push the tag to the remote repository.
5. Once the new tag is pushed, the CI will automatically build the RPM and upload it to the release
6. Optionally update the release with the description of the changes from the CHANGELOG
7. Install RPM on an IBM i machine  [ Install RPM ](contributing/rpm-install)
8. [Test TOBi](contributing/testing) on that IBM i.
9. Use [publish github action](https://github.com/IBM/ibmi-tobi/actions/workflows/publish_rpm.yml) to generate the `tobi.spec` and create a pull request on [rpm-specs repo](https://github.ibm.com/ibmi-oss/rpm-specs/).  Once the reviewer merges the `yum install tobi` will work.

## Versioning
The version number is defined in the `src/makei/__init__.py` file and is handled by `bump2version` package.
The format of the version number is `{major}.{minor}.{patch}`. For example, the version number is `2.4.6`.
