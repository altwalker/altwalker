=======================
Install GraphWalker CLI
=======================

AltWalker uses `GraphWalker <http://graphwalker.github.io/>`_ to generate paths
through your model(s). The GraphWalker CLI, which is a standalone jar file, is
required by AltWalker. To execute the jar file, you need to have Java installed
on your system.

AltWalker comes with a pre-installed version of GraphWalker CLI. If you prefer
to use a different version of GraphWalker, follow these instructions to install
it:

Run the following commands to install GraphWalker:


.. tab:: MacOS/Linux

    .. tab:: wget

        .. code-block:: console

            wget -q -O - https://raw.githubusercontent.com/altwalker/graphwalker-installer/main/install-graphwalker.py
            python install-graphwalker.py

    .. tab:: git

        .. code-block:: console

            git clone https://github.com/altwalker/graphwalker-installer.git
            cd graphwalker-installer
            python install-graphwalker.py

.. tab:: Windows

    .. code-block:: console

        git clone https://github.com/altwalker/graphwalker-installer.git
        cd graphwalker-installer
        python install-graphwalker.py


After installing GraphWalker, verify that you have installed the correct
version by running the following command:

.. command-output:: gw --version


The latest version of GraphWalker is:

.. program-output:: gw --version
    :ellipsis: 1


Checkout `graphwalker-installer <https://github.com/altwalker/graphwalker-installer>`_ for a more detailed tutorial.
