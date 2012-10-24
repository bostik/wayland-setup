#!/usr/bin/python3

import os
import sys
import subprocess
import shutil
import glob

_HOME = os.path.expanduser('~')

# Edit to match
SOURCES_ROOT_DIR = os.path.join(_HOME, 'kala')
SOURCES_BUILD_DIR = os.path.join(_HOME, 'build')

# Do not touch
APT_REPO_DIR = '/var/tmp/wayland-devel-repo'

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
    'cairo':        '1.12.2',
    'xkbcommon':    'xkbcommon-0.2.0',
    'mesa':         'e20a0f14b5fdbff9afa5d0d6ee35de8728f6a200',
    'wayland':      '1.0.0',
    'weston':       '1.0.0',
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
    subprocess.check_call(['dpkg-buildpackage', '-rfakeroot', '-b', '-uc', '-us'])
    os.chdir(_d)

def install_pkgs(pkgs=None):
    if pkgs is None:
        raise WaylandSetupError('ERROR: No packages defined')
    # Make sure we have the latest list
    apt_args = ['sudo', 'aptitude', 'update']
    subprocess.check_call(apt_args)
    #
    apt_args = ['sudo', 'aptitude', '-y', 'install']
    apt_args.extend(pkgs)
    subprocess.check_call(apt_args)


def set_repo_key():
    # Get key ID
    gpgout = subprocess.check_output(['/usr/bin/gpg',
        '--no-default-keyring',
        '--keyring', '/var/tmp/wayland-repo-key.pub',
        '--list-keys', 'wayland'])
    gpgout_s = str(gpgout)
    lines = gpgout_s.split('\n')
    keyline = lines[0]
    toks = keyline.split()
    len_id = toks[1]
    (keylen, keyid) = len_id.split('/')
    #
    # Append to repository config (*in* repo conf dir)
    confpath = os.path.join(APT_REPO_DIR, 'conf', 'distributions')
    f = open(confpath, 'a')
    f.write('SignWith: ' + keyid + '\n')
    f.close()

def create_key():
    print('Checking for repository signing key...')
    subprocess.check_call(['./apt/create-repo-key.sh'])


def import_debs():
    print('Importing debian files...')
    subprocess.check_call(['./apt/add-debs-to-repo.sh', SOURCES_BUILD_DIR])
    debfiles = glob.glob(SOURCES_BUILD_DIR + '/*.*')
    for df in debfiles:
        print('\t%s' % df)
        os.remove(df)

def wipe_build_dir():
    print('Recreating build dir: %s' % SOURCES_BUILD_DIR)
    if os.path.isdir(SOURCES_BUILD_DIR):
        shutil.rmtree(SOURCES_BUILD_DIR)
    os.mkdir(SOURCES_BUILD_DIR)

def wipe_apt_repo():
    print('Removing APT repository: %s' % APT_REPO_DIR)
    if os.path.isdir(APT_REPO_DIR):
        shutil.rmtree(APT_REPO_DIR)
    # Create anew
    os.mkdir(APT_REPO_DIR)
    repoconfdir = os.path.join(APT_REPO_DIR, 'conf')
    os.mkdir(repoconfdir)
    # Copy repo config files
    dist_file = './apt/repository.distributions'
    opts_file = './apt/repository.options'
    dist_file_tgt = os.path.join(repoconfdir, 'distributions')
    opts_file_tgt = os.path.join(repoconfdir, 'options')
    shutil.copyfile(dist_file, dist_file_tgt)
    shutil.copyfile(opts_file, opts_file_tgt)

def setup_apt_repo():
    print('Checking for APT repository config...')
    if not os.path.exists('/etc/apt/sources.list.d/wayland-local.list'):
        subprocess.check_call(['sudo', 'cp', 'apt/wayland-local.list',
                '/etc/apt/sources.list.d/'])

def purge_packages():
    print('Purging existing Wayland stack...')
    subprocess.check_call(['./apt/purge-packages.sh'])



# Let's go!
for t in TOOLS:
    check_for(t)
for r in SOURCE_GIT_REPOS:
    get_or_update_source(r)


# Calls an external script which deals with the generation,
# turns into no-op if key is already present.
# NOTE: imports the keys into user's GPG keyring. See comment below.
create_key()

# Purge everything in the system
purge_packages()

# Clear target
wipe_apt_repo()
setup_apt_repo()


# Extract key ID and use in repository configuration
# Thanks to reprepro<->gpgme interaction, we can't use the desired gpg
# command line arguments (or their library equivalents). This in turn
# means that the GPG key **MUST** be in the user's keyring. We've done
# this in create_key() so the signing key is available in this step.
set_repo_key()


# Reset build environment
wipe_build_dir()

# Build packages, import to repo, install required packages from there
build_package('xkbcommon')
import_debs()
install_pkgs(['libxkbcommon-dev'])

build_package('wayland')
import_debs()
install_pkgs(['libwayland-dev'])

build_package('libdrm')
import_debs()
install_pkgs(['libdrm-dev'])

build_package('mesa')
import_debs()
install_pkgs(['libgles2-mesa-dev', 'libegl1-mesa-dri',  'libgbm-dev',
    'mesa-common-dev', 'libegl1-mesa-dev'])

# Extra packages for cairo
install_pkgs(['libxt-dev', 'libfontconfig1-dev', 'libfreetype6-dev',
    'libxcb-shm0-dev'])

build_package('cairo')
import_debs()
install_pkgs(['libcairo2-dev'])

# Weston needs even more packages. Those not related to mesa are
# installed in separate step to keep the flow easier to follow.
install_pkgs(['libxcursor-dev', 'libmtdev-dev', 'libpam0g-dev'])

### Stop here while testing...
build_package('weston')
import_debs()


# Now we should have all the bits in place for testing...
install_pkgs(['weston'])

