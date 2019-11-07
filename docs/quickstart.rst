Quickstart
==========

In this Quickstart section you will learn how to create your tests project from scratch, from an
existing model or to generate a code template for your models and run your tests with AltWalker.

.. contents:: Table of Contents
    :local:
    :backlinks: none


Start from scratch
------------------

You can use the ``init`` command to generate a new project.

The ``init`` command creates a project directory and initialize a git repository.
The project contains a sample model (``test-project/models/default.json``)
that will help you get started, and a test package containing the template code
for the model (``test-poject/tests``).

.. tabs::

    .. group-tab:: Python

        .. code::

            $ altwalker init -l python test-project

        Using the ``-l python`` option will generate a python package containing the template code for the model (``test-poject/tests``).

    .. group-tab:: C#/.NET

        .. code::

            $ altwalker init -l c# test-project

        Using the ``-l c#`` option will generate a C# project referring ``AltWalker.Executor`` from nuget, a class for the model and ``Program.cs``.

        .. code::

            test-project/
                models/
                    default.json
                tests/
                    Program.cs
                    ModelName.cs
                    tests.csproj

        The ``Program.cs`` contains the entry point of the tests and starts the ``ExecutorService``.

        .. code-block:: c#

            public class Program {

                public static void Main(string[] args) {
                    ExecutorService service = new ExecutorService();
                    service.RegisterModel<DefaultModel>();
                    service.Run(args);
                }
            }

    .. group-tab:: Custom Executor

        .. code::

            $ altwalker init test-project

        Not using the ``-l`` options will generate an empty ``test-poject/tests`` directory.

.. note::

    If you don't want the ``init`` commnad to initialize a git repository use ``--no-git`` option.

To run the tests for the `default.json` model, run the following command:

.. tabs::

    .. group-tab:: Python

        .. code::

            $ cd test-project
            $ altwalker online tests -m models/default.json.json "random(edge_coverage(100))"


    .. group-tab:: C#/.NET

        .. code::

            $ cd test-project
            $ altwalker online -x c# tests -m models/default.json.json "random(edge_coverage(100))"


The above command runs the tests found within the ``tests`` folder, based on the model
defined in ``default.json`` and using the  ``random(edge_coverage(100))`` stop condition.

Start from an existing model
----------------------------

The ``init`` command creates a project directory with your model(s), generates the code
template for the model(s) and initialize a git repository.

To generate a project you should replace the ``path/to/model-name.json`` and run the
following command:

.. tabs::

    .. group-tab:: Python

        .. code::

            $ altwalker init -l python test-project -m path/to/model-name.json

    .. group-tab:: C#/.NET

        .. code::

            $ altwalker init -l c# test-project -m path/to/model-name.json

    .. group-tab:: Custom Executor

        .. code::

            $ altwalker init test-project -m path/to/model-name.json

        Not using the ``-l`` options will generate an empty ``test-poject/tests`` directory.


.. note::

    You can call the ``init`` command with multiple models.


To run the tests for the your model, replace ``model-name.json`` with the
name of you model file and run the following command:

.. tabs::

    .. group-tab:: Python

        .. code::

            $ cd test-project
            $ altwalker online tests -m models/model-name.json.json "random(edge_coverage(100))"


    .. group-tab:: C#/.NET

        .. code::

            $ cd test-project
            $ altwalker online -x c# tests -m models/model-name.json.json "random(edge_coverage(100))"


The above command runs the tests found within the ``tests`` folder, based on the model
defined in ``default.json`` and using the  ``random(edge_coverage(100))`` stop condition.


Generate a code template for your models
----------------------------------------

You can use the ``generate`` command to generate a new test package for your model(s).

.. tabs::

    .. group-tab:: Python

        .. code::

            $ altwalker generate -l python path/for/test-project/ -m path/to/models.json

        The ``generate`` command will generate a test package named ``tests`` containing the code
        template for the modele(s), inside the ``path/for/package/`` directory.

    .. group-tab:: C#/.NET

        .. code::

            $ altwalker generate -l c# path/for/test-project/ -m path/to/models.json

        The generate command creates ``path/for/test-project`` directory containing
        ``test-project.csproj`` file, ``Program.cs`` and the code template for the model(s).


Further Reading/Useful Links
----------------------------

Depending on how new you are to AltWalker you can:

- read about how to design your models on the :doc:`modeling` section
- read about how to structure your tests on the :doc:`tests-structure` section
- checkout the :doc:`examples`
- dig deeper into the :doc:`cli`.
