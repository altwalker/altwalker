============
Installation
============

* **Pythons**: Python 3.7, 3.8, 3.9, 3.10, 3.11, PyPy3
* **Platforms**: Unix/POSIX and Windows
* **PyPI package name**: `altwalker <https://pypi.org/project/altwalker/>`_

.. sidebar:: For Docker Users

    If you want to use AltWalker with Docker you can skip this section.

    Read more in the: :doc:`how-tos/run-tests-with-docker` section.


Prerequisites
=============

* `Python3 <https://www.python.org/>`_ (with pip3)
* `Java <https://openjdk.java.net/>`_
* `GraphWalker CLI <http://graphwalker.github.io/>`_ (Optional)
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


Install AltWalker
=================

To install ``altwalker`` run the following command in your command line:

.. code-block:: console

    $ pip install -U altwalker


Alternatively, if you have multiple Python versions installed, you can use the
following command to specify the Python version:

.. code-block:: console

    $ python<version> -m pip install -U altwalker


To check that you have installed the correct version of AltWalker, run the
following command:

.. command-output:: altwalker --version


Living on the edge
------------------

If you want to work with the latest code before it’s released, install
or update the code from the `develop` branch:

.. code-block:: console

    $ pip install -U git+https://github.com/altwalker/altwalker


Install .NET Core (Optional)
============================

.NET Core is required by AltWalker when you want to write your tests in
a .NET supported language.

* Install .NET Core Runtime - enables AltWalker to execute compiled
  tests. Preferred in production environment.
* Install .NET Core SDK -  enables AltWalker to use dotnet to compile
  and run your tests. Preferred in development environment.

The ``dotnet`` command needs to be available under ``/usr/bin/dotnet``.
Installing .NET Core with snap makes the ``dotnet`` command available
under a different path. In this case create a symbolic link:

.. code-block:: console

    $ ln -s /path/to/dotnet /usr/bin/dotnet


Install GraphWalker (Optional)
==============================

AltWalker includes a pre-installed version of GraphWalker. If you prefer to use
a different version of GraphWalker, please refer to the :doc:`advanced-usage/install-graphwalker` guide.
