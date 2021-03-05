=======================
Write your own executor
=======================

The AltWalker executor is responsible for executing your tests. AltWalker provides you with
a Python3 and C#/.NET executor by default. You can hook up your own executor via HTTP.

Your HTTP executor should be able to create a test execution context and execute tests.
The context is initialized with path to tests provided via load route.

.. contents:: Table of Contents
    :local:
    :backlinks: none


Executor Routes
===============

**Root URL**: ``/altwalker``


Load
----

Should load test code from a given path. AltWalker calls load with the ``TEST_PACKAGE`` argument given to the ``verify``, ``online`` and ``walk`` commands.

* **URL**: ``/load``
* **Method**: ``POST``
* **Data Params**:

  .. code-block:: json

    {
        "path": "..."
    }

* **Success Response**:

    * **Code**: ``200``

* **Error Response**:

    * **Codes**:

        * ``463``: Path Not Found
        * ``464``: Load Error (in case the path to load is invalid)

* **Sample Call**:

  .. code-block:: console

    $ curl -X POST -d '{"path": "path/to/my/tests"}}' -H 'Content-Type: application/json'  http://localhost:4200/altwalker/load


Reset
-----

Should reset the current execution context.

* **URL**: ``/reset``
* **Method**: ``PUT``
* **Success Response**:

    * **Code**: `200`

* **Error Response**:

    * **Codes**:

        * ``465``: No Test Code Loaded

* **Sample Call**:

  .. code-block:: console

    $ curl -X PUT http://localhost:4200/altwalker/reset


Has Model
---------

Should check if a model exists. Is used by the ``verify`` command.


* **URL**: ``/hasModel``
* **Method**: ``GET``
* **URL Params**:

    Required: ``name=[string]``

* **Success Response**:

    * **Code**: ``200``
    * **Content**:

      .. code-block:: json

        {
            "payload": {
                "hasModel": true
            }
        }

* **Sample Call**:

  .. code-block:: console

    $ curl http://localhost:4200/altwalker/hasModel?name="ModelName"


Has Step
--------

Should checks if a step exists. Is used by the ``verify`` command.

* **URL**: ``/hasStep``
* **Method**: ``GET``
* **URL Params**:

    Required: ``name=[string]``

    Optional: ``modelName=[string]``

    The ``modelName`` is not needed for ``setUpRun`` and ``tearDownRun``.

* **Success Response**:

    * **Code**: ``200``
    * **Content**:

      .. code-block:: json

        {
            "payload": {
                "hasStep": true
            }
        }

* **Sample Call**:

  .. code-block:: console

    $ curl http://localhost:4200/altwalker/hasStep?name="setUpRun"

  .. code-block:: console

    $ curl http://localhost:4200/altwalker/hasStep?name="setUpModel"&modelName="ModelName"


Execute Step
------------

Should executes the step. Is used by the ``online`` and ``walk`` commands.

* **URL**: ``/executeStep``
* **Method**: ``POST``
* **URL Params**:

    Required: ``name=[string]``

    Optional: ``modelName=[string]``

    The ``modelName`` is not needed for ``setUpRun`` and ``tearDownRun``.

* **Data Params**:

    .. code-block:: json

        {
            "data": {
                "key": "value"
            }
        }

    The data is a key value dictionary containing the data form the current model.

* **Success Response**:
    * **Code**: ``200``
    * **Content**:

      .. code-block:: json

        {
            "payload": {
                "output": "",
                "data": {
                },
                "result": {
                },
                "error": {
                    "message": "",
                    "trace": ""
                }
            }
        }

    The ``output`` is the output of the step. It is required.

    The ``data`` key from the response should be the data modified by your tests. It is not required.

    The ``result`` is the value returned by the step. It is not required. It can be of any type.

    The ``error`` key should be present only if the step failed.

* **Error Response**:

    * **Codes**:

        * ``460``: Model Not Found
        * ``461``: Step Not Found
        * ``462``: Invalid Step Handler (in case a method with the name of Step exists but requires invalid arguments)

* **Sample Call**:

  .. code-block:: console

    $ curl -X POST -d '{"data": {"key": "value"}}' -H 'Content-Type: application/json'  http://localhost:4200/altwalker/hasStep?name="setUpModel"&modelName="ModelName"


Error Status Codes
==================

In case of any error in the Http executor, a status code and a json body is expected by AltWalker.

* ``404``: Not Found (for unhandled urls)
* ``460``: Model Not Found
* ``461``: Step Not Found
* ``462``: Invalid Step Handler (in case a method with the name of Step exists but requires invalid arguments)
* ``463``: Path Not Found
* ``464``: Load Error (in case the path to load is invalid)
* ``465``: No Test Code Loaded
* ``500``: Unhandled Exception

**Response Body**:

.. code-block:: json

    {
        "error": {
            "message": "...",
            "trace": "..."
        }
    }


Using your executor
===================

.. code-block:: console

    $ altwalker online -x http --url http://localhost:4200/ -m path/to/model.json "generator(stop_condition())" path/to/my/tests


* ``-x http``

    Use the http executor.

* ``--url http://localhost:4200/``

    The url where your executor is listening.

* ``path/to/my/tests``

    The path to your tests, relative to your executor location. This is passed to your executor via POST ``/load``.


Further Reading/Useful Links
============================

Check :class:`altwalker.executor.HttpExecutor` to see the HttpExecutor client.
