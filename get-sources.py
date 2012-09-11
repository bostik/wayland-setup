#!/usr/bin/python3

import os
import sys
import subprocess

# Edit to match
SOURCES_ROOT_DIR = None


SOURCE_GIT_REPOS = {
    'cairo':        'git://anongit.freedesktop.org/git/cairo',
    'xkbcommon':    'git://anongit.freedesktop.org/xorg/lib/libxkbcommon',
    'mesa':         'git://anongit.freedesktop.org/mesa/mesa',
    'wayland':      'git://anongit.freedesktop.org/wayland/wayland',
    'weston':       'git://anongit.freedesktop.org/wayland/weston',
}

# Setup output suppression for subprocess.*
devnull = open('/dev/null', 'w')

# Nice custom error message provider
class WaylandSetupError(Exception):
    def __init__(self, msg=None):
        if msg:
            print('%s' % msg)



# We need to have certain tools already available
def check_for(cmd=None):
    if cmd is None:
        raise WaylandSetupError('%s: argument not given' % check_for.__name__)
    #
    sys.stdout.write('Checking for "%s" ... ' % cmd)
    try:
        subprocess.check_call(['which', cmd],
            stdout=devnull,
            stderr=devnull)
        sys.stdout.write('OK')
    except subprocess.CalledProcessError:
        sys.stdout.write('not found')
        pass
    finally:
        sys.stdout.write('\n')


def get_or_update_source(repo):
    if SOURCES_ROOT_DIR is None:
        raise WaylandSetupError('ERROR: directory for source not set.')
    _d = os.getcwd()
    reponame = os.path.basename(SOURCE_GIT_REPOS[repo])
    path = os.path.join(SOURCES_ROOT_DIR, reponame)
    if os.path.isdir(path):
        # Update to latest sources
        os.chdir(path)
        subprocess.check_call(['git', 'fetch'])
        os.chdir(_d)
    else:
        # Clone sources
        os.chdir(SOURCES_ROOT_DIR)
        subprocess.check_call(['git', 'clone', SOURCE_GIT_REPOS[repo]])
        os.chdir(_d)





# Let's go!
check_for('git')
for r in SOURCE_GIT_REPOS:
    get_or_update_source(r)


