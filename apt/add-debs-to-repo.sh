#!/bin/sh

REPODIR=/var/tmp/wayland-devel-repo
DEBDIR=$1

if [ "x$1" = "x" ]; then
    echo "DEBDIR not provided as first argument"
    exit 1
fi

if [ ! -d ${DEBDIR} ]; then
    echo "Directory ./build not present"
    echo "Are you trying to run script from wrong path?"
    exit 1
fi

# Running the repository creation commands from root of repo dir keeps
# things straightforward and simple
cd ${REPODIR}

# Add specified .deb files to repository
for f in ${DEBDIR}/*.deb; do
    reprepro includedeb wayland-local $f
done
