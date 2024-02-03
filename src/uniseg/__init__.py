"""Determine Unicode text segmentations. """

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass

# The version of the Unicode database used in the package
unidata_version = '15.0.0'
