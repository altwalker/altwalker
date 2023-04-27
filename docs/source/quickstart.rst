==========
Quickstart
==========

Eager to get started? This page gives a good introduction to AltWalker. It assumes
you already have AltWalker installed. If you do not, head over to the :doc:`installation` section.

In this section you will learn how to create a tests project from scratch or from
existing models, how to validate your models, how to validate your code and how to run
your tests with AltWalker.


Start from scratch
==================

You can use the ``init`` command to generate a new project.

The ``init`` command creates a project directory and initialize a git repository. The
project contains a sample model (``models/default.json``) that will help you get started,
and a test package containing the template code for the model (``tests/``).

.. tab:: Python

    .. code::

        $ altwalker init -l python test-project

    Using the ``-l python`` option will generate a python package containing the template code for the model (``tests/``).

    .. code::

        test-project/
        ├── models/
        │   ├── default.json
        └── tests/
            ├── __init__.py
            └── test.py

.. tab:: C#/.NET

    .. code::

        $ altwalker init -l c# test-project

    Using the ``-l c#`` option will generate a C# project referring ``AltWalker.Executor`` from Nuget, a class for the model and ``Program.cs``.

    .. code::

        test-project/
        ├── models/
        │   ├── default.json
        └── tests/
            ├── Program.cs
            └── tests.csproj

    The ``Program.cs`` contains the entry point of the tests and starts the ``ExecutorService``.

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

    If you don't want the ``init`` command to initialize a git repository use ``--no-git`` option.

To run the tests for the `default.json` model, run the following command:

.. tab:: Python

    .. code::

        $ cd test-project
        $ altwalker online tests -m models/default.json "random(edge_coverage(100))"

.. tab:: C#/.NET

    .. code::

        $ cd test-project
        $ altwalker online -x c# tests -m models/default.json "random(edge_coverage(100))"


The above command runs the tests found within the ``tests`` folder, based on the
model defined in ``default.json`` and using the ``random(edge_coverage(100))``
stop condition.


Start from existing models
==========================

You can use the ``init`` command to generate a new project form existing models.

The ``init`` command creates a project directory with your model(s),
generates the code template for the model(s) and initialize a git repository.

To generate a project you should replace the ``path/to/model-name.json`` and
run the following command:

.. tab:: Python

    .. code::

        $ altwalker init -l python test-project -m path/to/model-name.json

.. tab:: C#/.NET

    .. code::

        $ altwalker init -l dotnet test-project -m path/to/model-name.json


.. note::

    You can call the ``init`` command with multiple models.


To run the tests for the your model, replace ``model-name.json`` with the
name of you model file and run the following command:

.. tab:: Python

    .. code::

        $ cd test-project
        $ altwalker online tests -m models/model-name.json "random(edge_coverage(100))"


.. tab:: C#/.NET

    .. code::

        $ cd test-project
        $ altwalker online -x c# tests -m models/model-name.json "random(edge_coverage(100))"


The above command runs the tests found within the ``tests`` folder,
based on the model defined in ``default.json`` and using the
``random(edge_coverage(100))`` stop condition.


Check your models
=================

You can use the ``check`` command to check your models for issues.

.. code::

    $ altwalker check -m models/model-name.json "random(never)"


Verify your code
================

You can use the ``verify`` command to check your code against the models for issues.

.. tab:: Python

    .. code::

        $ altwalker verify tests -l python -m models/model-name.json

.. tab:: C#/.NET

    .. code::

        $ altwalker verify tests -l dotnet -m models/model-name.json


Further Reading/Useful Links
============================

Depending on how new you are to AltWalker you can:

- Read about how to design your models on the :doc:`core/modeling` section
- Read about how to structure your tests on the :doc:`core/tests-structure` section
- Checkout the :doc:`examples`
- Dig deeper into the :doc:`cli`
