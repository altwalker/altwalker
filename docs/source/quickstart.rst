==========
Quickstart
==========

Are you eager to get started with AltWalker? This page provides a good
introduction to the framework. It assumes that you have already installed
AltWalker. If you haven't, head over to the :doc:`installation` section.

In this section, you will learn how to create a new project from scratch or
existing models, validate your models, validate your code, and run your tests
with AltWalker.


Create a New Project
====================

You can use the ``init`` command to create a new project.

The ``init`` command creates a project directory and initializes a git
repository. The project contains a sample model (``models/default.json``) to
help you get started, and a test package containing the template code for the
model (``tests/``).

.. tab:: Python

    .. code::

        $ altwalker init -l python test-project

    Using the ``-l python`` option generates a Python package containing the template code for the model (``tests/``).

    .. code::

        test-project/
        ├── models/
        │   ├── default.json
        └── tests/
            ├── __init__.py
            └── test.py

.. tab:: C#/.NET

    .. code::

        $ altwalker init -l dotnet test-project

    Using the ``-l dotnet`` option generates a .NET/C# project referring to ``AltWalker.Executor`` from Nuget, a class for the model, and ``Program.cs``.

    .. code::

        test-project/
        ├── models/
        │   ├── default.json
        └── tests/
            ├── Program.cs
            └── tests.csproj

    ``Program.cs`` contains the entry point of the tests and starts the ``ExecutorService``.

    .. code-block:: c#

        public class Program
        {
            public static void Main(string[] args)
            {
                ExecutorService service = new ExecutorService();
                service.RegisterModel<DefaultModel>();
                service.Run(args);
            }
        }

.. note::

    If you don't want the ``init`` command to initialize a git repository, use the ``--no-git`` option.


To run the tests for the ``default.json`` model, run the following command:

.. tab:: Python

    .. code::

        cd test-project
        altwalker online tests -m models/default.json "random(edge_coverage(100))"

.. tab:: C#/.NET

    .. code::

        cd test-project
        altwalker online -l dotnet tests -m models/default.json "random(edge_coverage(100))"


The above command runs the tests found within the ``tests/`` folder, based on the
model defined in ``default.json`` and using the ``random(edge_coverage(100))``
stop condition.


Create a Project from Existing Models
=====================================

You can use the ``init`` command to create a new project from existing models.

The ``init`` command creates a project directory with your model(s),
generates the code template for the model(s), and initialize a git repository.

To generate a project, replace ``path/to/model-name.json`` and
run the following command:

.. tab:: Python

    .. code::

        altwalker init -l python test-project -m path/to/model-name.json

.. tab:: C#/.NET

    .. code::

        altwalker init -l dotnet test-project -m path/to/model-name.json


.. note::

    You can call the ``init`` command with multiple models.


To run the tests for the your model, replace ``model-name.json`` with the
name of you model file and run the following command:

.. tab:: Python

    .. code::

        cd test-project
        altwalker online tests -m models/model-name.json "random(edge_coverage(100))"


.. tab:: C#/.NET

    .. code::

        cd test-project
        altwalker online -l dotnet tests -m models/model-name.json "random(edge_coverage(100))"

The above command runs the tests found within the ``tests/`` folder, based on the
model defined in ``models/model-name.json`` and using the ``random(edge_coverage(100))``
stop condition.


Check your models
=================

You can use the ``check`` command to check your models for issues. This command
can detect errors, deadlocks, unreachable states, and other model issues.

.. code::

    altwalker check -m models/model-name.json "random(never)"


Verify your code
================

You can use the ``verify`` command to check your code against the models for
issues. This command can detect syntax errors, missing classes or methods, and
other issues in your code.

.. tab:: Python

    .. code::

        altwalker verify tests -l python -m models/model-name.json

.. tab:: C#/.NET

    .. code::

        altwalker verify tests -l dotnet -m models/model-name.json


Run your tests
==============

You can use the ``online`` command to run your tests based on the model defined
in your project.

.. tab:: Python

    .. code::

        altwalker online tests -m models/default.json "random(edge_coverage(100))"

.. tab:: C#/.NET

    .. code::

        altwalker online -l dotnet tests -m models/default.json "random(edge_coverage(100))"


Further Reading/Useful Links
============================

Depending on how new you are to AltWalker you can:

- Read about how to design your models on the :doc:`core/modeling` section.
- Read about how to structure your tests on the :doc:`core/tests-structure` section.
- Checkout the :doc:`examples`.
- Dig deeper into the :doc:`cli`.
