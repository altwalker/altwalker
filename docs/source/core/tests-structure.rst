Tests Structure
===============

To run tests using AltWalker you need a models and tests implementing
the models.

Usually your project will look like this:

.. code::

    test-project/
    ├── models/
    │   └── ...
    └── tests/
        └── ...

Inside the ``models`` directory you will keep your models, and inside the
``tests`` directory you will have a test package containing the implementation
of the models.

Now AltWalker supports two languages: Python and C#/.NET.


Structure
---------

.. tab:: Python

    AltWalker requires a python package (usually named ``tests``) and inside a python module named  ``test.py``.

    .. code::

        test-project/
        ├── models/
        │   └── ...
        └── tests/
            ├── __init__.py
            └── test.py

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

.. tab:: C#/.NET

    AltWalker requires a C# console application that depends on `AltWalker.Executor <https://www.nuget.org/packages/AltWalker.Executor/>`_ from NuGet and runs the ``ExecutorService``.

    .. code::

        test-project/
        ├── models/
        │   └── ...
        └── tests/
            ├── Program.cs
            └── test-project.csproj

    .. code-block:: c#

        /// Program.cs
        using Altom.AltWalker;

        namespace Test.Project
        {
            /// The implementation of the model named ModelA.
            public class ModelA
            {
                /// The implementation of the vertex named vertex_a.
                public void vertex_a() {}

                /// The implementation of the edge named edge_a
                public void edge_a() {}
            }

            /// The implementation of the model named ModelB.
            public class ModelB
            {
                /// The implementation of the vertex named vertex_b.
                public void vertex_b() {}

                /// The implementation of the edge named edge_b
                public void edge_b() {}
            }

            public class Program
            {
                public static void Main (string[] args)
                {
                    ExecutorService service = new ExecutorService();

                    service.RegisterModel<ModelA>();
                    service.RegisterModel<ModelB>();

                    service.Start(args);
                }
            }
        }

    The ``AltWalker.Executor`` targets .netstandard 2.0.

Fixtures
--------

AltWalker implements four test :term:`fixtures<Test Fixture>` inspired by JUnit and the python
``unittest`` module:

- ``setUpRun``: Will be executed first, before anything else.
- ``tearDownRun``: Will be executed last.
- ``beforeStep``: Will be executed before every step.
- ``afterStep``: Will be executed after every step.
- ``setUpModel``: Will be executed before executing any step from this model.
- ``tearDownModel``: Will be executed after executing all steps from this
  model.

All fixtures are optional.

When you define the ``beforeStep`` and ``afterStep`` fixtures within a model
class, these fixtures will specifically apply to that particular model. In other
words, they will only affect the steps executed within that model's context. This
provides a way to encapsulate and customize individual models, allowing you to
fine-tune the behavior of these fixtures for each model independently.

.. tab::  Python

    .. code-block:: python

        # tests/test.py

        def setUpRun():
            """Will be executed first, before anything else."""

        def tearDownRun():
            """Will be executed last, after anything else."""

        def beforeStep():
            """Will be executed before every step."""

        def afterStep():
            """Will be executed after every step."""


        class ModelA:

            def setUpModel(self):
                """Will be executed once before executing any step from this model."""

            def tearDownModel(self):
                """Will be executed once after executing all steps from this model."""

            def beforeStep():
                """Will be executed before every step from this model."""

            def afterStep():
                """Will be executed after every step from this model."""

            def vertex_a(self):
                pass

            def edge_a(self):
                pass

.. tab::  C#/.NET

    Define ``setUpRun``, ``tearDownRun``, ``beforeStep`` and ``afterStep`` inside a ``Setup`` class, and
    register it inside the executor service: ``ExecutorService.RegisterSetup<T>();``

    Define ``setUpModel``, ``tearDownModel``, ``beforeStep`` and ``afterStep`` inside the model class.

    .. code-block:: c#

        /// Program.cs
        using Altom.AltWalker;

        namespace Test.Project
        {
            public class Setup
            {
                /// Will be executed first, before anything else.
                public void setUpRun() {}

                /// Will be executed last, after anything else.
                public void tearDownRun() {}

                /// Will be executed before every step.
                public void beforeStep() {}

                /// Will be executed after every step.
                public void afterStep() {}
            }

            /// The implementation of the model named ModelA.
            public class ModelA
            {
                /// Will be executed once before executing any steps from this model
                public void setUpModel() {}

                /// Will be executed once after executing all steps from this model
                public void tearDownModel() {}

                /// Will be executed before every step from this model.
                public void beforeStep() {}

                /// Will be executed after every step from this model.
                public void afterStep() {}
            }

            public class Program
            {
                public static void Main (string[] args)
                {
                    ExecutorService service = new ExecutorService();

                    service.RegisterSetup<Setup>();
                    service.RegisterModel<ModelA>();

                    service.Start(args);
                }
            }
        }


Read/Update Graph Data
----------------------

If you are using the ``online`` command your test code has direct access to the
graphs execution context provided by GraphWalker.

In order to read/update the graph data from your tests, you need to define the
method with a parameter, and AltWalker will pass the graph data to your method.
This method is a way of executing actions from you test code.

Updating the graph data can affect the path generation so this feature in not
available in :ref:`core/running-tests:Offline Mode`.

.. tab:: Python

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

.. tab:: C#/.NET

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

    .. tab:: Python

        .. code-block:: python

            value = int(data["integer"])

    .. tab:: C#/.NET

        .. code-block:: c#

            int value = int.Parse(data["integer"]);


    * for boolean

    .. tab:: Python

        .. code-block:: python

            value = data["boolean"] == "true"

    .. tab:: C#/.NET

        .. code-block:: c#

            bool value = data["boolean"] == "true";


Verify your code
----------------

You can use the ``verify`` command to check your code against the models for issues.

.. tab:: Python

    .. code::

        $ altwalker verify tests -l python -m models/model-name.json

.. tab:: C#/.NET

    .. code::

        $ altwalker verify tests -l dotnet -m models/model-name.json
