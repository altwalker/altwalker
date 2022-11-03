============
Installation
============

* **Pythons**: Python 3.5, 3.6, 3.7, 3.8, 3.9, PyPy3
* **Platforms**: Unix/Posix and Windows
* **PyPI package name**: `altwalker <https://pypi.org/project/altwalker/>`_

.. sidebar:: For Docker Users

    If you want to use AltWalker with Docker you can skip this section.

    Read more in the: :doc:`how-tos/run-tests-with-docker` section.


Prerequisites
=============

* `Python3 <https://www.python.org/>`_ (with pip3)
* `Java 11 <https://openjdk.java.net/>`_
* `GraphWalker CLI <http://graphwalker.github.io/>`_
* `.NET Core <https://dotnet.microsoft.com/>`_ (Optional)
* `git <https://git-scm.com/>`_ (Optional)


Python
------

.. note::

    On **Windows**, make sure you add Python and Python Scripts in the Path from System Variables:

    * ``C:\Python<version>\`` (e.g., ``C:\Python39\``)
    * ``C:\Python<version>\Scripts\`` (e.g., ``C:\Python39\Scripts\``)

    And your local Python Scripts directory in the Path from User Variables:

    * ``C:\Users\<user-name>\AppData\Local\Programs\Python\Python<version>\Scripts\``


GraphWalker
-----------

AltWalker relies on `GraphWalker <http://graphwalker.github.io/>`_ to generate paths through your model(s).

AltWalker uses the GraphWalker CLI, the CLI is a standalone jar file. You
need to have Java 11 installed to be able to execute the jar file.

You need to download GraphWalker CLI  from `GitHub Releases <https://github.com/GraphWalker/graphwalker-project/releases>`_ and
create a script to run the jar file from the command line. We recommend
downloading the latest version of GraphWalker CLI.

To install GraphWalker you can run the following command:

.. tabs::
    .. group-tab:: MacOS/Linux

        .. code-block:: console

            $ wget -q -O - https://raw.githubusercontent.com/altwalker/graphwalker-installer/main/install-graphwalker.py
            $ python install-graphwalker.py


        or

        .. code-block:: console

            $ git clone https://github.com/altwalker/graphwalker-installer.git
            $ cd graphwalker-installer
            $ python install-graphwalker.py

    .. group-tab:: Windows

        .. code-block:: console

            > git clone https://github.com/altwalker/graphwalker-installer.git
            > cd graphwalker-installer
            > python install-graphwalker.py

Checkout `graphwalker-installer <https://github.com/altwalker/graphwalker-installer>`_ for a more detailed tutorial.

After installing GraphWalker check that you installed the correct version:

.. command-output:: gw --version

Currently the latest version is:

.. program-output:: gw --version
    :ellipsis: 1


Install ``altwalker``
=====================

To install ``altwalker`` run the following command in your command line:

.. code-block:: console

    $ pip3 install -U altwalker

Or:

.. code-block:: console

    $ python<version> -m pip install -U altwalker

Check that you installed the correct version:

.. command-output:: altwalker --version


Living on the edge
------------------

If you want to work with the latest code before it’s released, install
or update the code from the `develop` branch:

.. code-block:: console

    $ pip3 install -U git+https://github.com/altwalker/altwalker


Install .NET Core (Optional)
============================

.NET Core is required by AltWalker when you want to write your tests in
a .NET supported language.

- Install .NET Core Runtime - enables AltWalker to execute compiled
  tests. Preferred in production environment.
- Install .NET Core SDK -  enables AltWalker to use dotnet to compile
  and run your tests. Preferred in development environment.

The ``dotnet`` command needs to be available under ``/usr/bin/dotnet``.
Installing .NET Core with snap makes the ``dotnet`` command available
under a different path. In this case create a symbolic link:

.. code-block:: console

    $ ln -s /path/to/dotnet /usr/bin/dotnet
