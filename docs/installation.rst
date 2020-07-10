Installation
============

.. sidebar:: For Docker Users

    If you want to use AltWalker with Docker you can skip this section.

    Read more in the: :doc:`how-tos/run-tests-with-docker` section.

**Pythons**: Python 3.4, 3.5, 3.6, 3.7, 3.8, PyPy3

**Platforms**: Unix/Posix and Windows

**PyPI package name**: `altwalker <https://pypi.org/project/altwalker/>`_

Prerequisites
-------------

* `Python3 <https://www.python.org/>`_ (with pip3)
* `Java 8 <https://openjdk.java.net/>`_
* `GraphWalker CLI <http://graphwalker.github.io/>`_
* `.NET Core <https://dotnet.microsoft.com/>`_ (Optional)
* `git <https://git-scm.com/>`_ (Optional)

Python
~~~~~~

On Windows, make sure you add Python in the Path from System Variables:

* ``C:\Python<version>\`` (e.g., ``C:\Python37``)
* ``C:\Python<version>\Scripts\`` (e.g., ``C:\Python37\Scripts\``)

And in the Path from User Variables:

* ``C:\Users\user.name\AppData\Local\Programs\Python\Python<version>\Scripts``

GraphWalker
~~~~~~~~~~~

AltWalker relies on `Graphwalker <http://graphwalker.github.io/>`_ to generate paths through your model(s).

AltWalker uses the GraphWalker CLI, the CLI is a standalone jar file. You
need to have Java 8 installed to be able to execute the jar file.

You need to download GraphWalker CLI  from `GitHub Releases <https://github.com/GraphWalker/graphwalker-project/releases>`_ and
create a script to run the jar file from the command line. We recommend
downloading the latest version of GraphWalker CLI.

To install GraphWalker you can run the following command:

.. tabs::
    .. group-tab:: MacOS/Linux

        .. code-block:: console

            $ wget https://github.com/GraphWalker/graphwalker-project/releases/download/4.2.0/graphwalker-cli-4.2.0.jar && \
              mkdir -p ~/graphwalker && \
              mv graphwalker-cli-4.2.0.jar ~/graphwalker/ && \
              echo -e '#!/bin/bash\njava -jar ~/graphwalker/graphwalker-cli-4.2.0.jar "$@"' > ~/graphwalker/graphwalker-cli.sh && \
              chmod +x ~/graphwalker/graphwalker-cli.sh && \
              ln -s ~/graphwalker/graphwalker-cli.sh /usr/local/bin/gw

        Here is a more detailed `tutorial <https://github.com/GraphWalker/graphwalker-project/wiki/Command-Line-Tool#creating-a-script-facilitating-command-line-handling-on-a-linux-machine>`_ for macOS/linux.

    .. group-tab:: Windows

        .. code-block:: console

            > setx PATH "%PATH%;C:\graphwalker" & :: Adds graphwalker to current user PATH
              cd C:\
              mkdir graphwalker
              cd graphwalker
              powershell -Command "[Net.ServicePointManager]::SecurityProtocol = 'tls12'; Invoke-WebRequest -Uri 'https://github.com/GraphWalker/graphwalker-project/releases/download/4.2.0/graphwalker-cli-4.2.0.jar' -outfile 'graphwalker-cli-4.2.0.jar'" & :: Downloads graphwalker using powershell command Invoke-Request
              @echo off
              @echo @echo off> gw.bat
              @echo java -jar C:\graphwalker\graphwalker-cli-4.2.0.jar %*>> gw.bat
              @echo on

After installing GraphWalker check that you installed the correct version:

.. command-output:: gw --version

Currently the latest version is:

.. program-output:: gw --version
    :ellipsis: 1

Install ``altwalker``
---------------------

To install ``altwalker`` run the following command in your command line:

.. code-block:: console

    $ pip3 install -U altwalker

Or:

.. code-block:: console

    $ python<version> -m pip install -U altwalker

Check that you installed the correct version:

.. command-output:: altwalker --version

Living on the edge
~~~~~~~~~~~~~~~~~~

If you want to work with the latest code before it’s released, install
or update the code from the `develop` branch:

.. code-block:: console

    $ pip3 install -U git+https://gitlab.com/altom/altwalker/altwalker

Install .NET Core (Optional)
----------------------------

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
