How to Build RPM
----------------

## Setup the RPM Build Environment

### 1. Check that you have rpmbuild installed

We will need `rpmbuild` to build RPM from the SPEC file. If you do not have rpm-build installed, use the following command to install it.

```bash
yum install rpm-build
```

### 2. Create directories for RPM building under home

The instruction below will create a `rpmbuild` directory under your home directory to build RPMs.

```bash
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
```

### 3. Build TOBi RPM

* Create a new draft version named `v{r.v.m}` where `{r.v.m}` is the new version number
* make sure you update `tobi.spec` to the new release level
* publish the release so the curl command below will find it
* Execute the following commands

```bash
export TOBI_VERSION=r.v.m 
cd ~/rpmbuild
curl "https://raw.githubusercontent.com/IBM/ibmi-tobi/v${TOBI_VERSION}/tobi.spec" -o SPECS/tobi.spec
rpmbuild -ba SPECS/tobi.SPEC
```

* The rpm is now created under `~/rpmbuild/RPMS/PPC64` directory.
* upload to the version and republish it

### 4. Install TOBi RPM

* Run the follow to install TOBi from the RPM
* The TOBI_VERSION should be the same as above, if it is still set there is no need to do this again.
* The `rpm -e` command removes the previously installed version of TOBi so that we can install the new one without conflict.

```bash
export TOBI_VERSION=r.v.m 
rpm -e `rpm -qa | grep -i tobi`
rpm -i ~/rpmbuild/RPMS/PPC64/tobi-${TOBI_VERSION}-0.ibmi7.3.ppc64.rpm
```

### 5. Test TOBi RPM

Then test according to the [Testing instructions](contributing/testing.md)