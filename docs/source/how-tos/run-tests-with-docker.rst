=============================
How to: Run tests with Docker
=============================

.. meta::
   :keywords: AltWalker, Model-Based Testing, C#, .NET, Docker

If you want to skip the installation of AltWalker you could use one of
`our docker images <https://hub.docker.com/r/altwalker/altwalker>`_.


Create a ``Dockerfile`` for your project
----------------------------------------

To use altwalker with docker add the following ``Dockerfile`` in the root
of your project.

.. tab:: Python

    .. code-block:: docker
        :caption: Dockerfile

        FROM altwalker/altwalker:latest

        COPY . /test-project
        WORKDIR  /test-project

        RUN touch requirements.txt
        RUN python3 -m pip install -r requirements.txt

        # If you have other dependencies you can install them here.

.. tab:: C#/.NET

    .. code-block:: docker
        :caption: Dockerfile

        FROM altwalker/altwalker:latest-dotnet-2.1

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

.. tab:: Python

    .. code-block:: console

        $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
            /bin/bash -c 'python3 -m pip install -r requirements.txt && altwalker online [...]'

    If you don't have any python dependencies you can remove the ``python3 -m pip install -r requirements.txt``.

    .. code-block:: console

        $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
            altwalker online [...]

.. tab:: C#/.NET

    .. code-block:: console

        $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest-dotnet-2.1 \
            altwalker online [...]


Example:

.. tab:: Python

    .. code-block:: console

        $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest \
            /bin/bash -c 'python3 -m pip install -r requirements.txt && altwalker online tests -m models/default.json "random(vertex_coverage(100))"'

.. tab:: C#/.NET

    .. code-block:: console

        $ docker run -it -v "$(pwd):/test-project" -w "/test-project" altwalker/altwalker:latest-dotnet-2.1 \
            altwalker online tests -m models/default.json "random(vertex_coverage(100))"
