#!/usr/bin/env bash
export VERSION=${GITHUB_REF#refs/tags/v} 
echo "VERSION ${VERSION}"
python3 tools/release/generate_spec.py ${VERSION} CHANGELOG True
cd ~
mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,BUILDROOT}
cp tobi.spec rpmbuild/SPECS
PATH=/QOpenSys/pkgs/bin:/QOpenSys/usr/bin:/usr/bin time /QOpenSys/pkgs/bin/rpmbuild -ba --define '_topdir ~/rpmbuild' rpmbuild/SPECS/tobi.spec
export RPM_FILE_PATH=$(find . -name '*.rpm' -print -quit)
echo "RPM ${RPM_FILE_PATH}"
mv ${RPM_FILE_PATH } tobi.rpm