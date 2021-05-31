========================
Log data from your tests
========================

Logging information is critical to the development and maintenance of your tests. AltWalker
collects stdout and returned data from your tests.

.. contents:: Table of Contents
    :local:
    :backlinks: none


Stdout
------

AltWalker captures stdout data from each test and outputs it to the stdout of altwalker cli,
or to a file if ``--report-file`` option is used.


.. tabs::

    .. group-tab:: Python

        .. code-block:: python

            class Simple:
                def vertex_a(self, *args):
                    print("Simple.vertex_a")

        .. code-block:: console
            :emphasize-lines: 3

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Output:
            Simple.vertex_a



    .. group-tab:: C#/.NET

        .. code-block:: c#

            public class WalletModel
            {
                public void vertex_a()
                {
                    Trace.WriteLine("Simple.vertex_a");
                }
            }

        .. code-block:: console
            :emphasize-lines: 3

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Output:
            Simple.vertex_a

    .. group-tab:: Custom Executor

        Execute Step response:

        .. code-block:: json

            {
                "payload": {
                    "output": "Simple.vertex_a"
                }
            }

        .. code-block:: console
            :emphasize-lines: 3

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Output:
            Simple.vertex_a



Returned data from tests
------------------------

AltWalker captures return value from each test and outputs it to the stdout of altwalker
cli, or to a file if ``--report-file`` option is used.

.. tabs::

    .. group-tab:: Python

        Return any json serializable object

        .. code-block:: python

            class Simple:
                def vertex_a(self, *args):
                    return { "key" : "value" }

        .. code-block:: console
            :emphasize-lines: 3-5

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Result:
            {
                "key": "value"
            }

    .. group-tab:: C#/.NET

        Return any json serializable object

        .. code-block:: c#

            public class WalletModel
            {
                public object vertex_a()
                {
                    return new Dictionary<string, string> () { {"key", "value" } };
                }
            }

        .. code-block:: console
            :emphasize-lines: 3-5

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Result:
            {
                "key": "value"
            }


    .. group-tab:: Custom Executor

        Execute Step response:

        .. code-block:: json

            {
                "payload": {
                    "result": {"key" : "value"}
                }
            }

        .. code-block:: console
            :emphasize-lines: 3-5

            [2020-04-27 14:26:20.731201] Simple.vertex_a Status: PASSED
            Result:
            {
                "key": "value"
            }
