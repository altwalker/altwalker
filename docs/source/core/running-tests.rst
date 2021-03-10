=============
Running Tests
=============

After you finished modeling and written the required test code it's time
to run your tests.

AltWalker supports two ways or running tests:

1. Online Mode: With the ``online`` command.

2. Offline Mode: With the ``offline`` and ``walk`` commands.


.. contents:: Table of Contents
    :local:
    :backlinks: none


Online Mode
-----------

With the online mode (*on the fly mode*) the test generation and execution happen at the same time.

The online mode can be roughly described by de following algorithm:

.. code::

    while path not completed:
        get step
        execute step

In order to run your tests in online mode you need to use the ``online`` command:

.. tabs::

    .. group-tab:: Python

        .. code::

            $ altwalker online tests -m models/default.json "random(vertex_coverage)"

    .. group-tab:: C#/.NET

        .. code::

            $ altwalker online tests -l dotnet -m models/default.json "random(vertex_coverage)"


**Example**

.. code::

    $ altwalker online tests -m models/default.json "random(vertex_coverage(100))"
    Running:
    [2019-08-06 16:28:44.030077] ModelName.vertex_A Running
    [2019-08-06 16:28:44.030940] ModelName.vertex_A Status: PASSED

    [2019-08-06 16:28:44.048492] ModelName.edge_A Running
    [2019-08-06 16:28:44.048729] ModelName.edge_A Status: PASSED

    [2019-08-06 16:28:44.064495] ModelName.vertex_B Running
    [2019-08-06 16:28:44.064746] ModelName.vertex_B Status: PASSED

    Statistics:

    Model Coverage..................100%
    Number of Models...................1
    Completed Models...................1
    Failed Models......................0
    Incomplete Models..................0
    Not Executed Models................0

    Edge Coverage...................100%
    Number of Edges....................1
    Visited Edges......................1
    Unvisited Edges....................0

    Vertex Coverage.................100%
    Number of Vertices.................2
    Visited Vertices...................2
    Unvisited Vertices.................0

    Status:  PASS

**Further Reading/Useful Links**

* :ref:`Online Command Documentation <cli:altwalker offline>`

Offline Mode
------------

With the offline mode the path generation is done once and the path sequences
is save in a file and then AltWalker use that file to execute the test.

You can use the offline mode to generate test cases that you want run
frequently.

Generating paths
~~~~~~~~~~~~~~~~

A path is a list of steps; the steps will be executed in the order they appear.

The template for an *path*:

.. code-block:: json

    [
        {
            "id": "<The id of the first step>",
            "name": "<The name of the first step>",
            "modelName": "<The model name of the first step>",
        },
        {
            "id": "<The id of the second step>",
            "name": "<The name of the second step>",
            "modelName": "<The model name of the second step>",
        }
    ]

**Example**

.. code-block:: json

    [
        {
            "id": "v_0",
            "modelName": "LoginModel",
            "name": "v_start"
        },
        {
            "id": "e_0",
            "modelName": "LoginModel",
            "name": "e_open_app"
        },
        {
            "id": "v_1",
            "modelName": "LoginModel",
            "name": "v_app"
        }
    ]

You can use the ``offline`` command to generate a test path (test case).

.. code::

    $ altwalker offline -m models/default.json "random(vertex_coverage)" -f steps.json

.. note::

    As mentioned in the :doc:`path-generation` section the ``never`` and ``time_duration``
    stop conditions are not allowed with the *offline mode*; because the path generation
    happens before the test execution:

      * the path generation must stop so we can't use the ``never`` stop condition
      * we don't have information about the time of execution so we can't use the ``time_duration`` stop condition

You can also write your own paths.

Running paths
~~~~~~~~~~~~~

After you generated a test path and saved it to a file you can run it with the ``walk``
command.

.. tabs::

    .. group-tab:: Python

        .. code::

            $ altwalker walk tests steps.json

    .. group-tab:: C#/.NET

        .. code::

            $ altwalker walk tests steps.json -l dotnet

The ``walk`` command will read the file and execute the steps.

.. warning::

    In offline mode you will not have access to the graph data. Because the path is
    already generate you can't execute actions from your test code.

**Example**

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

**Further Reading/Useful Links**

* :ref:`Offline Command Documentation <cli:altwalker offline>`
* :ref:`Walk Command Documentation <cli:altwalker walk>`
