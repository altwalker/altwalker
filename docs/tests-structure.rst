Tests Structure
===============

To run tests using AltWalker you need a model(s) and tests implementing
the model(s).

Usually your project will look like this:

.. code::

    project-root/
        models/
            ...
        tests/
            ...

Inside the ``models`` directory you will keep your model(s), and inside the
``tests`` directory you will have a test package containing the implementation
of the model(s).

Now AltWalker supports two languages: Python and C#/.NET.


.. contents:: Table of Contents
    :local:
    :backlinks: none


Structure
---------

.. tabs::

    .. group-tab:: Python

        AltWalker requires a python package (usually named ``tests``) and inside a python module named  ``test.py``.

        .. code::

            project-root/
                tests/
                    __init__.py
                    test.py

        Inside ``test.py`` each model is implemented in a class, and each
        vertex/edge in a method inside the class.

        .. code-block:: python

            # tests/test.py

            class ModelA:
                """The implementation of the model named ModelA."""

                def vertex_a(self):
                    """The implementation of the vertex named vertex_a form ModelA."""

                def edge_a(self):
                    """The implementation of the edge named edge_a form ModelA."""


            class ModelB:
                """The implementation of the model named ModelB."""

                def vertex_b(self):
                    """The implementation of the vertex named vertex_b form ModelB."""

                def edge_b(self):
                    """The implementation of the edge named edge_b form ModelB."""

    .. group-tab:: C#/.NET

        AltWalker requires a c# console application that depends on `altwalker.executor <https://www.nuget.org/packages/AltWalker.Executor/>`_ from NuGet and runs the ``ExecutorService``.

        .. code-block:: c#

            /// The implementation of the model named ModelA.
            public class ModelA {

                /// The implementation of the vertex named vertex_a.
                public void vertex_a() {}

                /// The implementation of the edge named edge_a
                public void edge_a() {}
            }

            public class Program {
                    public static void Main (string[] args) {
                        ExecutorService service = new ExecutorService();
                        service.RegisterSetup<Setup>();
                        service.Start(args);
                    }
                }

        The ``altwalker.executor`` targets .netstandard 2.0.

Fixtures
--------

AltWalker implements four test fixtures inspired by JUnit and the python
unittest module:

- ``setUpRun``: Will be executed first, before anything else.
- ``tearDownRun``: Will be executed last.
- ``setUpModel``: Will be executed before executing any step from this model.
- ``tearDownModel``: Will be executed after executing all steps from this
    model.

All fixtures are optional.

.. tabs::

    .. group-tab:: Python

        .. code-block:: python

            # tests/test.py

            def setUpRun():
                """Will be executed first, before anything else."""

            def tearDownRun():
                """Will be executed last."""


            class ModelA:

                def setUpModel(self):
                    """Will be executed before executing any step from this model."""

                def tearDownModel(self):
                    """Will be executed after executing all steps from this model."""

                def vertex_a(self):
                    pass

                def edge_a(self):
                    pass

    .. group-tab:: C#/.NET

        Define ``setUpModel`` and ``tearDownModel`` inside the model class.

        Define ``setUpRun`` and ``tearDownRun`` inside a Setup class, and register it inside the executor service: ``ExecutorService.RegisterSetup<T>();``

        .. code-block:: c#

            /// The implementation of the model named ModelA.
            public class ModelA {

                /// Will be executed before executing all steps from this model
                public void setUpModel() {}

                /// Will be executed after executing all steps from this model
                public void tearDownModel() {}
            }

            public class Startup {

                /// Will be executed first, before anything else.
                public void setUpRun() {}

                /// Will be executed first, after anything else.
                public void tearDownRun() {}
            }

            public class Program {
                public static void Main (string[] args) {
                    ExecutorService service = new ExecutorService();

                    service.RegisterModel<MyModel>();
                    service.RegisterSetup<Setup>();

                    service.Start(args);
                }
            }

Read/Update Graph Data
----------------------

If you are using the ``online`` command your test code has direct access to the
graphs execution context provided by GraphWalker.

In order to read/update the graph data from your tests, you need to define the
method with a parameter, and AltWalker will pass the graph data to your method.
This method is a way of executing actions from you test code.

.. tabs::

    .. group-tab:: Python

        The second parameter will be a ``dict`` object, that object allows you to read and update the graph data.

        .. code-block:: python

            def element_method(self, data):
                """A simple example of a method for a vertex/edge inside a model.

                Args:
                    data: AltWalker will pass a ``dict`` object.
                """

                # to get the value for a single key
                value = data["key"]

                # to set a new value for a key
                data["strVariable"] = "new_value"
                data["intVariable"] = 1
                data["boolVariable"] = True


    .. group-tab:: C#/.NET

        The second parameter will be a ``IDictionary<string, dynamic>`` object, that object allows you to read and update the graph data.

        .. code-block:: c#

            /// A simple example of a method for a vertex/edge inside a model.
            public void element_method(IDictionary<string, dynamic> data)
            {
                // to get the value for a single key
                string value = data["key"]

                // to set a new value for a key
                data["strVariable"] = "new_value"
                data["intVariable"] = 1
                data["boolVariable"] = true
            }

.. warning::

    Note that you can set keys to string, integer or boolean values, but GraphWalker will always return strings.

    So you have to convert your values back to there type.

    * for integers

    .. tabs::

        .. group-tab:: Python

            .. code-block:: python

                value = int(data["integer"])

        .. group-tab:: C#/.NET

            .. code-block:: c#

                int value = int.Parse(data["integer"]);


    * for boolean

    .. tabs::

        .. group-tab:: Python

            .. code-block:: python

                value = data["boolean"] == "true"

        .. group-tab:: C#/.NET

            .. code-block:: c#

                bool value = data["boolean"] == "true";
