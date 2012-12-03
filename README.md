Debian-packaged Wayland-on-DRM autobuilder script
=================================================


This script builds, packages and automatically installs Wayland 1.0 with
DRM stack for testing and development purposes.

*TARGET SYSTEM:*    Debian Sid

*TARGET AUDIENCE:*  Developers

May work with a recent Ubuntu. Not tested.


*REQUIREMENTS:*     Blanket sudo privileges
In practice, something like this:
```
# Allow members of group sudo to execute any command
%sudo   ALL=NOPASSWD: ALL
```

WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!
-----------------------------------------------------

Running this script will butcher and cannibalise your installation.
Use only on a spare computer which you plan to test Wayland on.


Packaging rules have been lifted from Debian, and modified to suit
this single purpose. Original maintainers have not been involved. This
setup script has no warranty of any kind: if something breaks, you get
to keep the pieces.

That said, you can return to a known baseline state by manually
executing './apt/purge-packages.sh'


Happy hacking!

