======================
Command Line Interface
======================

Help
----

Getting help on version, available commands, arguments or option names:

.. code-block:: console

    $ altwalker -v/--version
    $ altwalker -h/--help # show help message and all available commands
    $ altwalker command_name -h/--help # show help message for the specified command


Possible exit codes
-------------------

Running ``altwalker`` can result in five  different exit codes:

* **Exit Code 0:** Tests were successfully run and passed.
* **Exit Code 1:** Tests were successfully run and failed.
* **Exit Code 2:** Command line errors.
* **Exit Code 3:** GraphWalker errors.
* **Exit Code 4:** AltWalker internal errors.

========
Commands
========

.. click:: altwalker.cli:cli
   :prog: altwalker
   :commands: init, generate, check, verify, online, offline, walk

----

.. click:: altwalker.cli:init
   :prog: altwalker init
   :show-nested:


**Examples:**

.. code-block:: console

    $ altwalker init test-project

The command will create a directory named ``test-project`` with the following structure::

    test-project/
        .git
        models/
            default.json
        tests/
            __init__.py
            test.py

* **test-project**: The project root directory.
* **models**: A directory containing the models files (``.json`` or ``.graphml``).
* **tests**: A python package containing the test code.
* **tests/tests.py**: A python module containing the code for the models.

If you don't want ``test-project`` to be git repository run the command with ``--no-git``:

.. code-block:: console

    $ altwalker init test-project --no-git


.. note::
    If you don't have ``git`` installed on your machine use the ``--no-git`` flag.


If you specify models (with the ``-m/--models`` option) ``init`` will copy the
models in the  ``models`` directory and ``test.py`` will contain a template
with all the classes and methods needed for
the models:

.. code-block:: console

    $ altwalker init test-project -m ./first.json -m ./second.json


The ``test-project`` directory will have the following structure::

    test-project/
        .git
        models/
            fisrt.json
            second.json
        tests/
            __init__.py
            test.py


----

.. click:: altwalker.cli:generate
   :prog: altwalker generate
   :show-nested:


**Examples**:

.. code-block:: console

    $ altwalker generate test-project -m models/models.json

The command will create a directory named ``test`` with the following structure::

    test-project/
        tests/
            __init__.py
            test.py

For a `models.json` file with a simple model named ``Model``, with an edge named ``edge_name``
and a vertex named ``vertex_name``, ``test.py`` will containe::

    class Model:

        def vertex_name(self):
            pass

        def edge_name(self):
            pass


The ``-m/--model`` option is required and can be used multiple times. And the ``generate`` command
will generate a class for each model you provide.


----

.. click:: altwalker.cli:check
   :prog: altwalker check
   :show-nested:

**Example:**

For the ``model`` option you need to pass a ``model_path`` and a ``stop_condtion``.

* **model_path**: Is the file (``.json`` or ``.graphml``) containing the model(s).
* **stop_condition**: Is a string that specifies the generator and the stop condition.

    For example ``random(never)``, ``a_star(reached_edge(edge_name))``, where ``random``
    , ``a_star`` are the generators and ``never``, ``reached_edge(edge_name)`` are the
    stop conditions.

    For more details and a list of all available options read the
    `GraphWalker Documentation <http://graphwalker.github.io/generators_and_stop_conditions/>`_.

The ``-m/--model`` is required but you can use it multiple times to provide multiple models:

.. code-block:: console

    $ altwalker check -m login.json "random(never)" -m shop.json "random(never)"
    No issues found with the model(s).


----

.. click:: altwalker.cli:verify
   :prog: altwalker verify
   :show-nested:


**Examples:**

.. code-block:: console

    $ altwalker verify tests -m models.json
    No issues found with the code.

The ``verify`` command will check that every element from the provided models is
implemented in the ``tests/test.py`` (models as classes and vertices/edges as methods inside
the model class).

If methods or classes are missing the command will return a list of errors:

.. code-block:: console

    $ altwalker verify tests -m models.json
    AltWalker Error: Expected to find vertex_0 method in class Model_A.
    Expected to find vertex_1 method in class Model_A.
    Expected to find vertex_2 method in class Model_A.
    Expected to find class Model_B.
    Expected to find vertex_0 method in class Model_B.
    Expected to find vertex_1 method in class Model_B.
    Expected to find edge_0 method in class Model_B.
    Expected to find edge_1 method in class Model_B.


----

.. click:: altwalker.cli:online
   :prog: altwalker online
   :show-nested:

**Examples:**

For the ``-m/--model`` option you need to pass a ``model_path`` and a ``stop_condtion``.

* **model_path**: Is the file (``.json`` or ``.graphml``) containing the model(s).
* **stop_condition**: Is a string that specifies the generator and the stop condition.

    For example ``random(never)``, ``a_star(reached_edge(edge_name))``, where ``random``
    , ``a_star`` are the generators and ``never``, ``reached_edge(edge_name)`` are the
    stop conditions.

    For more details and a list of all available options read the
    `GraphWalker Documentation <http://graphwalker.github.io/generators_and_stop_conditions/>`_.


The ``-m/--model`` is required but you can use it multiple times to provide multiple models.

For example:

.. code-block:: console

    $ altwalker online tests -m models.json "random(vertex_coverage(30))" -p 9999
    Running:
    [2019-02-07 12:56:42.986142] ModelName.vertex_A Running
    [2019-02-07 12:56:42.986559] ModelName.vertex_A Status: PASSED
    Statistics:
    {
        "edgeCoverage": 0,
        "edgesNotVisited": [
            {
                "edgeId": "e0",
                "edgeName": "edge_A",
                "modelName": "ModelName"
            }
        ],
        "failedFixtures": [],
        "failedStep": {},
        "steps": [
            {
                "id": "v0",
                "modelName": "ModelName",
                "name": "vertex_A",
                "status": true
            }
        ],
        "totalCompletedNumberOfModels": 1,
        "totalFailedNumberOfModels": 0,
        "totalIncompleteNumberOfModels": 0,
        "totalNotExecutedNumberOfModels": 0,
        "totalNumberOfEdges": 1,
        "totalNumberOfModels": 1,
        "totalNumberOfUnvisitedEdges": 1,
        "totalNumberOfUnvisitedVertices": 1,
        "totalNumberOfVertices": 2,
        "totalNumberOfVisitedEdges": 0,
        "totalNumberOfVisitedVertices": 1,
        "vertexCoverage": 50,
        "verticesNotVisited": [
            {
                "modelName": "ModelName",
                "vertexId": "v1",
                "vertexName": "vertex_B"
            }
        ]
    }
    Status: True

If you use the ``-o/--verbose`` flag, the command will print for each step the ``data``
(the data for the current module) and ``properties`` (the properties of the current step
defined in the model):

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

If you use the ``-u/--unvisited`` flag, the command will print for each step the
current list of all unvisited elements:

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

----

.. click:: altwalker.cli:offline
   :prog: altwalker offline
   :show-nested:

.. note::

    If you are using in your models guards and in the test code you update the models data,
    the offline command may produce invalid paths.

**Examples:**

For the ``-m/--model`` option you need to pass a ``model_path`` and a ``stop_condtion``.

* **model_path**: Is the file (``.json`` or ``.graphml``) containing the model(s).
* **stop_condition**: Is a string that specifies the generator and the stop condition.

    For example ``random(reached_vertex(vertex_name))``, ``a_star(reached_edge(edge_name))``, where ``random``
    , ``a_star`` are the generators and ``reached_vertex(vertex_name)``, ``reached_edge(edge_name)`` are the
    stop conditions.

    For more details and a list of all available options read the
    `GraphWalker Documentation <http://graphwalker.github.io/generators_and_stop_conditions/>`_.


.. note::

    The ``never`` and ``time_duration`` stop condition is not usable with the ``offline``
    command only with the ``online`` command.


The ``-m/--model`` is required but you can use it multiple times to provide multiple models.


Example:

.. code-block:: console

    $ altwalker offline -m models.json "random(vertex_coverage(100))"
    [
        {
            "id": "v0",
            "modelName": "Example",
            "name": "start_vertex"
        },
        {
            "id": "e0",
            "modelName": "Example",
            "name": "from_start_to_end"
        },
        {
            "id": "v1",
            "modelName": "Example",
            "name": "end_vertex"
        }
    ]



If you want to save the steps in a ``.json`` file you can use the ``-f/--output-file <FILE_NAME>``
option:

.. code-block:: console

    $ altwalker offline -m models.json "random(vertex_coverage(100))" -f steps.json



If you use the ``-o/--verbose`` flag, the command will add for each step
``data`` (the data for the current module) and ``properties``
(the properties of the current step defined in the model)::

    {
        "id": "v0",
        "name": "vertex_A",
        "modelName": "ModelName",

        "data": {
            "a": "0",
            "b": "0",
            "itemsInCart": "0"
        },
        "properties": []
    }

If you use the ``-u/--unvisited`` flag, the command will add for each step the
current list of all unvisited elements, the number of elements and the number
of unvisited elements::

    {
        "id": "v0",
        "name": "vertex_A",
        "modelName": "ModelName",

        "numberOfElements": 3,
        "numberOfUnvisitedElements": 3,
        "unvisitedElements": [
            {
                "elementId": "v0",
                "elementName": "vertex_A"
            },
            {
                "elementId": "v1",
                "elementName": "vertex_B"
            },
            {
                "elementId": "e0",
                "elementName": "edge_A"
            }
        ]
    }

----

.. click:: altwalker.cli:walk
   :prog: altwalker walk
   :show-nested:

**Examples:**

Usually the ``walk`` command will execute a path generated by the ``offline`` command,
but it can execute any list of steps, that respects that format.

A simple example:

.. code-block:: console

    $ altwalker walk tests steps.json
    Running:
    [2019-02-15 17:18:09.593955] ModelName.vertex_A Running
    [2019-02-15 17:18:09.594358] ModelName.vertex_A Status: PASSED
    [2019-02-15 17:18:09.594424] ModelName.edge_A Running
    [2019-02-15 17:18:09.594537] ModelName.edge_A Status: PASSED
    [2019-02-15 17:18:09.594597] ModelName.vertex_B Running
    [2019-02-15 17:18:09.594708] ModelName.vertex_B Status: PASSED

    Statistics:
    {
        "failedFixtures": [],
        "failedStep": {
            "id": "v1",
            "modelName": "ModelName",
            "name": "vertex_B",
            "status": false
        },
        "steps": [
            {
                "id": "v0",
                "modelName": "ModelName",
                "name": "vertex_A"
            },
            {
                "id": "e0",
                "modelName": "ModelName",
                "name": "edge_A"
            },
            {
                "id": "v1",
                "modelName": "ModelName",
                "name": "vertex_B"
            }
        ]
    }
    Status: False
