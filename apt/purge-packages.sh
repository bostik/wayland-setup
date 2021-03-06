#!/bin/bash
#
# Bash? The '+=' syntax for appending to variable is not supported in
# plain old /bin/sh.

# Removing these packages clears the entire Wayland development stack
BASEPKGS="libglapi-mesa mesa-common-dev libgl1-mesa-dri libdrm2 "
BASEPKGS+="libxkbcommon0 libkms1 libegl1-mesa-drivers libcairo2 "
BASEPKGS+="libegl1-mesa libegl1-mesa-drivers"

# Remove everything
sudo aptitude -y purge ${BASEPKGS}
