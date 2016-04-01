# System import
import os
from setuptools import find_packages, setup


# Select appropriate modules
scripts = []
pkgdata = {}
release_info = {}
execfile(os.path.join(os.path.dirname(__file__), 'python', 'bv_capsul_ex', 'info.py'),
         release_info)

# Build the setup
setup(
    name="{0}".format(release_info["NAME"]),
    description=release_info["DESCRIPTION"],
    long_description=release_info["LONG_DESCRIPTION"],
    license=release_info["LICENSE"],
    classifiers=release_info["CLASSIFIERS"],
    author=release_info["AUTHOR"],
    author_email=release_info["AUTHOR_EMAIL"],
    version=release_info["VERSION"],
    url=release_info["URL"],
    # All modules are in the python directory
    package_dir = {'': 'python'},
    packages=find_packages('python'),
    package_data=pkgdata,
    platforms=release_info["PLATFORMS"],
    extras_require=release_info["EXTRA_REQUIRES"],
    install_requires=release_info["REQUIRES"],
    scripts=scripts
)
