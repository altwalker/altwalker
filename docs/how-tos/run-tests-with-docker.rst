=====================
Run tests with Docker
=====================

.. meta::
   :keywords: AltWalker, Model-Based Testing, C#, .NET, Docker

If you want to skip the installaton of AltWalker you chould use one of
`our docker images <https://hub.docker.com/r/altwalker/altwalker>`_.

.. contents:: Table of Contents
    :local:
    :backlinks: none

Create a ``Dockerfile`` for your project
----------------------------------------

To use altwalker with docker add the following ``Dockerfile`` in the root
of your project.

.. tabs::

    .. group-tab:: Python

        .. code-block:: docker
            :caption: Dockerfile

            FROM altwalker/altwalker:latest

            COPY . /test-porject
            WORKDIR  /test-porject

            RUN touch requirements.txt
            RUN python3 -m pip install -r requirements.txt

            # If you have other dependencies you can install them here.

    .. group-tab:: C#/.NET

        .. code-block:: docker
            :caption: Dockerfile

            FROM altwalker/altwalker:latest-dotnet-2.2

            COPY . /my-tests
            WORKDIR  /my-tests

            # If you have other dependencies you can install them here.

            RUN dotnet build tests


You can then build and run the Docker image:

.. code-block:: console

    $ docker build -t my-tests .
    $ docker run -it my-tests altwalker online [...]


Example:

.. code-block:: console

    $ docker build -t my-tests .
    $ docker run -it my-tests altwalker \
        online tests -m models/default.json "random(vertex_coverage(100))"


Run your tests as a script
--------------------------

For many projects you may find it inconvenient to write a complete
``Dockerfile``. In such cases, you can run you tests as a script by
using the AltWalker Docker image directly:

.. tabs::

    .. group-tab:: Python

        .. code-block:: console

            $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
                /bin/bash -c 'python3 -m pip install -r requirements.txt && altwalker online [...]'

        If you don't have any python dependencies you can remove the ``python3 -m pip install -r requirements.txt``.

        .. code-block:: console

            $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
               altwalker online [...]

    .. group-tab:: C#/.NET

        .. code-block:: console

            $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest-dotnet-2.2 \
                altwalker online [...]


Example:

.. tabs::

    .. group-tab:: Python

        .. code-block:: console

            $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
                /bin/bash -c 'python3 -m pip install -r requirements.txt && altwalker online tests -m models/default.json "random(vertex_coverage(100))"'

    .. group-tab:: C#/.NET

        .. code-block:: console

            $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest-dotnet-2.2 \
                altwalker online tests -m models/default.json "random(vertex_coverage(100))"
