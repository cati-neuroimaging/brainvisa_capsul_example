# Capsul current version
version_major = 0
version_minor = 0
version_micro = 1

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(version_major, version_minor, version_micro)
CAPSUL_MIN_VERSION = '2.0.0'

brainvisa_dependencies = [
    'capsul',
]

brainvisa_build_model = 'pure_python'

# Expected by setup.py: the status of the project
CLASSIFIERS = ["Development Status :: 5 - Production/Stable",
               "Environment :: Console",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering",
               "Topic :: Utilities"]

# Project descriptions
description = "Example of how to use CAPSUL within BrainVISA framework"
long_description = None

# Main setup parameters
NAME = "brainvisa_capsul_example"
ORGANISATION = "CEA"
MAINTAINER = ""
MAINTAINER_EMAIL = ""
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = ""
DOWNLOAD_URL = ""
LICENSE = "CeCILL-B"
CLASSIFIERS = CLASSIFIERS
AUTHOR = ""
AUTHOR_EMAIL = ""
PLATFORMS = "OS Independent"
ISRELEASE = ""
VERSION = __version__
PROVIDES = [NAME]
REQUIRES = [
    "capsul>={0}".format(CAPSUL_MIN_VERSION),
]
EXTRA_REQUIRES = {}


