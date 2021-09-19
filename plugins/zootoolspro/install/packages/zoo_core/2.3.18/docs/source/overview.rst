
Overview
####################################################

Welcome to Zoo Core Reference documentation.
Zoo Core contains all general use code from handling
Zootools preference storage, Qt(PySide2 etc) extension's,
general utilities and much more.


Who is this documentation for?
----------------------------------------

This documentation is intended for **Technical director's** who
are looking to develop for Zootools or wishing to use zoocore for
general use outside of the Zootools Pro ecosystem.

Using Zoo Core
----------------------------------------
Zoo core while it's part of Zootools Pro eco system which handles automatically
loading zoocore can still be used as a standalone package.

First clone the repository::
    git clone https://github.com/dsparrow27/zoocore


Now once you're in a python environment with zoocore
we need to setup some environment variables

I will only use relative paths here so replace with absolute paths

.. code-block:: python

    os.environ["PYTHONPATH"] += "./zoocore/thirdparty;"
    os.environ["ZOO_BASE_PATHS"] = "./zoocore;"
    os.environ["ZOO_ICON_PATHS"] = "./icons;"
    os.environ["ZOO_COMMAND_LIB"] = "./zoo/libs/command/library;"

What each environment Refer's too.

================ ===========================================================================
ZOO_BASE_PATHS         Root absolute path for zoocore, used by our reloading code.

ZOO_ICON_PATHS    Directory for zoo icons which can contain multiple paths.

ZOO_COMMAND_LIB  Command library path which can contain multiple paths.
================ ===========================================================================