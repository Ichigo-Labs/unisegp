================
Unicode Versions
================


:mod:`unicodedata2` and :mod:`uniseg`
=====================================

:mod:`unicodedata2` [#]_ is a backport project of the standard
:mod:`unicodedata` [#]_ library.  It provides the same functionality of the
:mod:`unicodedata` which is based on the (almost) latest Unicode versions on
every Python version.

:mod:`uniseg` uses some :mod:`unicodedata` functions (:func:`category`,
:func:`east_asian_width`, etc.) on its internal processes.  At the current
release, these functions look providing the same results through all the
supported Python versions, so that the text segmentation works fine dispite of
that the algorithm is implemented under the different version of the Unicode.

This compatibility feature is not guaranteed through further releases of the
module though.  It will be a good practice to install :mod:`unicodedata2` which
supports the same Unicode version as :mod:`uniseg` does.

:mod:`uniseg` uses :mod:`unicodedata2` instead of the built-in
:mod:`unicodedata` module when :mod:`unicodedata2` is found on the system.
Note that it does not check whether its versions match though.

You can see the Unicode version which :mod:`uniseg` supports by checking
:data:`uniseg.unidata_version`.

.. [#] `unicodedata2 · PyPI <https://pypi.org/project/unicodedata2/>`_
.. [#] `unicodedata — Unicode Database — Python 3.9.20 documentation
    <https://docs.python.org/3.9/library/unicodedata.html>`_


Python Versions and :data:`unicodedata.unidata_version`
=======================================================

======  ===================================
Python  :data:`unicodedata.unidata_version`
======  ===================================
3.13    "15.1.0"
3.12    "15.0.0"
3.11    "14.0.0"
3.10    "13.0.0"
3.9     "13.0.0"
======  ===================================
