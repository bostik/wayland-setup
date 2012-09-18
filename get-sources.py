#!/usr/bin/python3

import os
import sys
import subprocess
import shutil

# Edit to match
SOURCES_ROOT_DIR = '/home/bostik/kala'
SOURCES_BUILD_DIR = '/home/bostik/build'

# Tools
TOOLS = set(['git', 'quilt', 'dpkg-buildpackage', 'fakeroot', 'reprepro'])

# Keys match the dirnames under p/
SOURCE_GIT_REPOS = {
    'cairo':        'git://anongit.freedesktop.org/git/cairo',
    'xkbcommon':    'git://anongit.freedesktop.org/xorg/lib/libxkbcommon',
    'mesa':         'git://anongit.freedesktop.org/mesa/mesa',
    'wayland':      'git://anongit.freedesktop.org/wayland/wayland',
    'weston':       'git://anongit.freedesktop.org/wayland/weston',
    'libdrm':       'git://anongit.freedesktop.org/mesa/drm',
}

# Yeah yeah, single dict and tuples for values instead of this...
SOURCE_GIT_REVS = {
    'cairo':        'git://anongit.freedesktop.org/git/cairo',
    'xkbcommon':    'origin/master',
    'mesa':         'origin/9.0',
    'wayland':      '0.95.0',
    'weston':       '0.95.0',
    'libdrm':       '2.4.39',
}

# Setup output suppression for subprocess.*
devnull = open('/dev/null', 'w')

# Nice custom error message provider
class WaylandSetupError(Exception):
    def __init__(self, msg=None):
        if msg:
            print('\n%s\n' % msg)



# We need to have certain tools already available
def check_for(cmd=None):
    if cmd is None:
        raise WaylandSetupError('%s: argument not given' % check_for.__name__)
    #
    found = False
    sys.stdout.write('Checking for "%s" ... ' % cmd)
    try:
        subprocess.check_call(['which', cmd],
            stdout=devnull,
            stderr=devnull)
        sys.stdout.write('OK')
        found = True
    except subprocess.CalledProcessError:
        sys.stdout.write('not found')
        pass
    finally:
        sys.stdout.write('\n')
    #
    if not found:
        raise WaylandSetupError('"%s" not found, can not continue' % cmd)


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

def debian_dir_path(root=None, pkg=None):
    if root is None:
        raise WaylandSetupError('ERROR: root dir not specified')
    if pkg is None:
        raise WaylandSetupError('ERROR: package name not specified')
    return os.path.join(root, 'p', pkg)



def build_package(pkg):
    if SOURCES_BUILD_DIR is None:
        raise WaylandSetupError('ERROR: directory for builds not set.')
    _d = os.getcwd()
    repodir = os.path.basename(SOURCE_GIT_REPOS[pkg])
    path = os.path.join(SOURCES_ROOT_DIR, repodir)
    if not os.path.isdir(path):
        raise WaylandSetupError('ERROR: not a source dir: %s' % path)
    #
    builddir = os.path.join(SOURCES_BUILD_DIR, repodir)
    os.chdir(path)
    # Remove previous one, if it exists
    if os.path.isdir(builddir):
        shutil.rmtree(builddir)
    # Export naked sources
    _pfx = '--prefix=%s/' % repodir
    git_p = subprocess.Popen(['git', 'archive', '--format=tar', _pfx,
            SOURCE_GIT_REVS[pkg]], stdout=subprocess.PIPE)
    tar_p = subprocess.Popen(['tar', '-C', SOURCES_BUILD_DIR, '-xf', '-'],
            stdin=git_p.stdout, stdout=None)
    git_p.stdout.close() # For SIGPIPE handling
    tar_p.communicate()
    #
    # Copy debianisation files in place
    debdir = debian_dir_path(_d, pkg)
    shutil.copytree(debdir, builddir + '/debian')
    #
    os.chdir(builddir)
    subprocess.check_call(['dpkg-buildpackage', '-rfakeroot', '-b', '-uc'])
    os.chdir(_d)

def import_debs():
    subprocess.check_call(['./apt/add-debs-to-repo.sh', SOURCES_BUILD_DIR])
    debfiles = glob.glob(SOURCES_BUILD_DIR + '/*.*')
    for df in debfiles:
        os.remove(df)



# Let's go!
for t in TOOLS:
    check_for(t)
for r in SOURCE_GIT_REPOS:
    get_or_update_source(r)

# Build packages, import to repo, install required packages from there
build_package('xkbcommon')
import_debs()

#build_package('wayland')
#build_package('libdrm')
#build_package('mesa')
#build_package('weston')

