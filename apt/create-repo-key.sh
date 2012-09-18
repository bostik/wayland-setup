#!/bin/sh

# There is no way to use aptitude without signing packages any longer.
# Very nice idea (and one I generally applaud), but using *local*,
# *non-networked* repositories should be possible without repository
# signing. Ah well, minor usability corner-cases regularly take back
# seat when dealing with security issues.

# Only create the key(s) once
if [ -e /var/tmp/wayland-repo-key.sec ]; then
    exit 0
fi

# Create an unencrypted (no passphrase) GPG key
/usr/bin/gpg --gen-key --batch apt/gpg-key-params

# Feed public key to APT
/usr/bin/gpg --no-default-keyring \
    --keyring /var/tmp/wayland-repo-key.pub \
    --armor --export wayland | sudo apt-key add -

