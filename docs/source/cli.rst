======================
Command Line Interface
======================

----------
Invocation
----------

.. code-block:: console

    altwalker [...]

You can also invoke the command through the Python interpreter from the
command line:

.. code-block:: console

    python -m altwalker [...]


----
Help
----

Getting help on version, available commands, arguments or option names:

.. code-block:: console

    $ altwalker -v/--version

    $ # show help message and all available commands
    $ altwalker -h/--help

    $ # show help message for the specified command
    $ altwalker command_name -h/--help


-------------------
Possible exit codes
-------------------

Running ``altwalker`` can result in five  different exit codes:

* **Exit Code 0:** Tests were successfully run and passed.
* **Exit Code 1:** Tests were successfully run and failed.
* **Exit Code 2:** Command line errors.
* **Exit Code 3:** GraphWalker errors.
* **Exit Code 4:** AltWalker internal errors.


--------
Commands
--------

.. click:: altwalker.cli:cli
   :prog: altwalker
   :commands: init, generate, check, verify, online, offline, walk


-------------------------------------------------------------------

.. click:: altwalker.cli:init
   :prog: altwalker init
   :nested:

.. note::

    The ``-m/--model`` is **not required** and can be used multiple times to provide
    multiple models.

**Examples**

.. code-block:: console

    $ altwalker init test-project -l python

The command will create a directory named ``test-project`` with the following
structure::

    test-project/
    ├── .git/
    ├── models/
    │   └── default.json
    └── tests/
        ├── __init__.py
        └── test.py

* **test-project**: The project root directory.
* **models**: A directory containing the models files
  (``.json`` or ``.graphml``).
* **tests**: A python package containing the test code.
* **tests/tests.py**: A python module containing the code for the model(s).

If you don't want ``test-project`` to be git repository run the command with
``--no-git``:

.. code-block:: console

    altwalker init test-project -l python --no-git

.. note::
    If you don't have ``git`` installed on your machine use the ``--no-git`` flag.

If you specify models (with the ``-m/--models`` option) ``init`` will copy the
models in the  ``models`` directory and ``test.py`` will contain a template
with all the classes and methods needed for the models:

.. code-block:: console

    altwalker init test-project -m ./first.json -m ./second.json -l python

The ``test-project`` directory will have the following structure::

    test-project/
    ├── .git/
    ├── models/
    │   ├── first.json
    │   └── second.json
    └── tests/
        ├── __init__.py
        └── test.py


-------------------------------------------------------------------

.. click:: altwalker.cli:generate
   :prog: altwalker generate
   :nested:

.. note::

    The ``-m/--model`` is **required** and can be used multiple times to provide
    multiple models. The ``generate`` command will generate a class for each model
    you provide.

**Examples**

.. code-block:: console

    altwalker generate . -m models/models.json

The command will create a directory named ``test`` with the following
structure::

    test-project/
    ├── models/
    │   ├── models.json
    └── tests/
        ├── __init__.py
        └── test.py

For a `models.json` file with a simple model named ``Model``, with an edge
named ``edge_name`` and a vertex named ``vertex_name``, ``test.py`` will
contain::

    class Model:

        def vertex_name(self):
            pass

        def edge_name(self):
            pass


-------------------------------------------------------------------

.. click:: altwalker.cli:check
   :prog: altwalker check
   :nested:

.. note::

    The ``-m/--model`` is **required** and can be use it multiple times to provide
    multiple models.

.. note::

    For the ``-m/--model`` option you need to pass a ``model_path`` and a ``stop_condition``.

      * ``model_path``: Is the file (``.json`` or ``.graphml``) containing the model(s).
      * ``stop_condition``: Is a string that specifies the generator and the stop condition.

    For example: ``"random(never)"``, ``"a_star(reached_edge(edge_name))"`` where ``random`` and ``a_star``
    are the generators; ``never`` and ``reached_edge(edge_name)`` are the stop conditions.

    Further Reading/Useful Links:

      * :doc:`core/path-generation`
      * `GraphWalker Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Generators-and-stop-conditions>`_.

**Examples**

.. command-output:: altwalker check -m models/blog-navigation.json "random(never)" -m models/blog-post.json "random(never)"
    :cwd: _static/

If the models are not valid the command will return a list of errors:

.. command-output:: altwalker check -m models/invalid.json "random(never)"
    :cwd: _static/
    :returncode: 4


-------------------------------------------------------------------

.. click:: altwalker.cli:verify
   :prog: altwalker verify
   :nested:

.. note::

    The ``-m/--model`` is **required** and can be use it multiple times to provide
    multiple models.

**Examples**

.. code-block:: console

    $ altwalker verify tests -m models/default.json
    Verifying code against models:

        * ModelName [PASSED]

    No issues found with the code.


The ``verify`` command will check that every element from the provided
models is implemented in the ``tests/test.py`` (models as classes and
vertices/edges as methods inside the model class).

If methods or classes are missing the command will return a list of errors
and code suggestions to fix the errors:

.. code-block:: console

    Verifying code against models:

    * ModelName [FAILED]

        Expected to find method 'edge_A' in class 'ModelName'.
        Expected to find method 'vertex_B' in class 'ModelName'.
        Expected to find method 'vertex_A' in class 'ModelName'.
        Expected to find class 'ModelName'.


    Code suggestions:

    # Append the following class to your test file.

    class ModelName:

        def edge_A(self):
            pass

        def vertex_A(self):
            pass

        def vertex_B(self):
            pass

If you don't need the code suggestions you can add ``--no-suggestions`` flag.

.. code-block:: console

    Verifying code against models:

    * ModelName [FAILED]

        Expected to find method 'edge_A' in class 'ModelName'.
        Expected to find method 'vertex_B' in class 'ModelName'.
        Expected to find method 'vertex_A' in class 'ModelName'.
        Expected to find class 'ModelName'.


-------------------------------------------------------------------

.. click:: altwalker.cli:online
   :prog: altwalker online
   :nested:

.. note::

    The ``-m/--model`` is **required** and can be use it multiple times to provide
    multiple models.

.. note::

    For the ``-m/--model`` option you need to pass a ``model_path`` and a ``stop_condition``.

      * ``model_path``: Is the file (``.json`` or ``.graphml``) containing the model(s).
      * ``stop_condition``: Is a string that specifies the generator and the stop condition.

    For example: ``"random(never)"``, ``"a_star(reached_edge(edge_name))"`` where ``random`` and ``a_star``
    are the generators; ``never`` and ``reached_edge(edge_name)`` are the stop conditions.

    Further Reading/Useful Links:

      * :doc:`core/path-generation`
      * `GraphWalker Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Generators-and-stop-conditions>`_.


**Examples**

.. code-block:: console

    $ altwalker online tests -m models.json "random(vertex_coverage(30))" -p 9999
    Running:
    [2019-02-07 12:56:42.986142] ModelName.vertex_A Running
    [2019-02-07 12:56:42.986559] ModelName.vertex_A Status: PASSED
    ...
    Status: True

If you use the ``-o/--verbose`` flag, the command will print for each step
the ``data`` (the data for the current module) and ``properties`` (the
properties of the current step defined in the model):

.. code-block:: console

    [2019-02-18 12:53:13.721322] ModelName.vertex_A Running
    Data:
    {
        "a": "0",
        "b": "0",
        "itemsInCart": "0"
    }
    Properties:
    {
        "x": 1,
        "y": 2
    }

If you use the ``-u/--unvisited`` flag, the command will print for each
step the current list of all unvisited elements:

.. code-block:: console

    [2019-02-18 12:55:07.173081] ModelName.vertex_A Running
    Unvisited Elements:
    [
        {
            "elementId": "v1",
            "elementName": "vertex_B"
        },
        {
            "elementId": "e0",
            "elementName": "edge_A"
        }
    ]


-------------------------------------------------------------------

.. click:: altwalker.cli:offline
   :prog: altwalker offline
   :nested:

.. note::

    The ``-m/--model`` is **required** and can be use it multiple times to provide
    multiple models.

.. note::

    For the ``-m/--model`` option you need to pass a ``model_path`` and a ``stop_condition``.

      * ``model_path``: Is the file (``.json`` or ``.graphml``) containing the model(s).
      * ``stop_condition``: Is a string that specifies the generator and the stop condition.

    For example: ``"random(never)"``, ``"a_star(reached_edge(edge_name))"`` where ``random`` and ``a_star``
    are the generators; ``never`` and ``reached_edge(edge_name)`` are the stop conditions.

    Further Reading/Useful Links:

      * :doc:`core/path-generation`
      * `GraphWalker Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Generators-and-stop-conditions>`_.

.. warning::

    1. If you are using in your model(s) guards and in the test code you update the models data,
    the ``offline`` command may produce invalid paths.

    2. The ``never`` and ``time_duration`` stop condition is not usable with the ``offline``
    command only with the ``online`` command.

**Example**

.. command-output:: altwalker offline -m models/login.json "random(length(5))"
    :cwd: _static/
    :returncode: 0

If you want to save the steps in a ``.json`` file you can use the
``-f/--output-file <FILE_NAME>`` option:

.. code-block:: console

    altwalker offline -m models/login.json "random(length(5))" --output-file steps.json

If you use the ``-o/--verbose`` flag, the command will add for each step
``data`` (the data for the current module), ``actions`` (the actions
of the current step as defined in the model) and ``properties`` (the properties
of the current step as defined in the model).

.. command-output:: altwalker offline -m models/login.json "random(length(5))" --verbose
    :cwd: _static/
    :returncode: 0

If you use the ``-u/--unvisited`` flag, the command will add for each step the
current list of all unvisited elements, the number of elements and the number
of unvisited elements.

.. command-output:: altwalker offline -m models/login.json "random(length(1))" --unvisited
    :cwd: _static/
    :returncode: 0


-------------------------------------------------------------------

.. click:: altwalker.cli:walk
   :prog: altwalker walk
   :nested:

**Examples:**

Usually the ``walk`` command will execute a path generated by the ``offline``
command, but it can execute any list of steps, that respects that format.

.. code-block:: console

    $ altwalker walk tests steps.json
    Running:
    [2019-02-15 17:18:09.593955] ModelName.vertex_A Running
    [2019-02-15 17:18:09.594358] ModelName.vertex_A Status: PASSED
    [2019-02-15 17:18:09.594424] ModelName.edge_A Running
    [2019-02-15 17:18:09.594537] ModelName.edge_A Status: PASSED
    [2019-02-15 17:18:09.594597] ModelName.vertex_B Running
    [2019-02-15 17:18:09.594708] ModelName.vertex_B Status: PASSED

    Status: True
