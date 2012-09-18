#!/bin/sh

REPODIR=/var/tmp/wayland-devel-repo
DEBDIR=$(pwd)/build

if [ ! -d ${DEBDIR} ]; then
    echo "Directory ./build not present"
    echo "Are you trying to run script from wrong path?"
    exit 1
fi

# Prepare repository
if [ ! -d ${REPODIR} ]; then
    mkdir ${REPODIR}
    mkdir ${REPODIR}/conf
    cp apt/repository.options ${REPODIR}/conf/options
    cp apt/repository.distributions ${REPODIR}/conf/distributions
fi

# Running the repository creation commands from root of repo dir keeps
# things straightforward and simple
cd ${REPODIR}

# Add specified .deb files to repository
for f in ${DEBDIR}/*.deb; do
    reprepro includedeb wayland-development $f
done

# Eventually make sure that the packages are cleaned up after insert
echo "WOULD RUN: rm -f ${DEBDIR}/*.deb"

