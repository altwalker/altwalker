=================
API Documentation
=================

This part of the documentation lists the full API reference of all
public classes and functions.

.. contents:: Table of Contents
    :local:
    :backlinks: none

.. module:: altwalker


Walker
======

.. module:: altwalker.walker

.. currentmodule:: altwalker.walker

.. autoclass:: Walker
    :members:

**Examples**

You can run the tests using the :func:`Walker.run` method::

    walker = Walker(...)
    walker.run()

Or iterating over a :class:`Walker` object::

    walker = Walker(...)
    for step in walker:
        # do something with the step

.. autofunction:: create_walker


Planner
=======

.. module:: altwalker.planner

.. currentmodule:: altwalker.planner

The role of a ``Planner`` is to determine the next step to be executed by
the ``Executor``.

There are two Planners:

    * :class:`OnlinePlanner`:

        Uses GraphWalker online mode to generate the test path.

        This method allows the test code to directly interact with GraphWalker
        and modify the model data. A dictionary with model data will be passed
        as a the first argument to any method/function form the test code
        by :class:`~altwalker.walker.Walker` class.

    * :class:`OfflinePlanner`:

        Uses a sequence of steps to generate the test path.

        The sequence of path can be generated using
        the :func:`~altwalker.graphwalker.offline` function.

.. autoclass:: OnlinePlanner
    :members:

.. autoclass:: OfflinePlanner
    :members:

.. autofunction:: create_planner


Executor
========

.. module:: altwalker.executor


.. currentmodule:: altwalker.executor

The role of the executor is to handle the test execution. Every executor
should have all the methods form the :class:`~altwalker.executor.Executor`.


.. autoclass:: Executor
    :members:


.. autoclass:: HttpExecutor

    .. automethod:: has_model

    .. automethod:: has_step

    .. automethod:: execute_step

    .. automethod:: reset

    .. automethod:: kill


.. autoclass:: PythonExecutor
    :members:


.. autoclass:: DotnetExecutor
    :members:
    :inherited-members:


.. autofunction:: create_http_executor


.. autofunction:: create_python_executor


.. autofunction:: create_dotnet_executor


.. autofunction:: create_executor


Reporter
========

.. module:: altwalker.reporter

.. currentmodule:: altwalker.reporter

The role of the reporter is to report the results of a test run, a
reporter method is called by the :class:`~altwalker.walker.Walker`
for different events:

    * :func:`~Reporter.start` - called at the beginning of each run.
    * :func:`~Reporter.end` - called at the end of each run.
    * :func:`~Reporter.step_start` - called before executing each step.
    * :func:`~Reporter.step_end` - called after executing each step.
    * :func:`~Reporter.report` - it should return a report if the reporter
      generates on (e.g. the :class:`PrintReporter` or
      :class:`FileReporter` don't generate any report, they only log data).
      It's not called by the :class:`~altwalker.walker.Walker`.

Every reporter should have all this methods, you can inherit them from
:class:`Reporter` and overwrite only the methods you want.

.. autoclass:: Reporter
    :members:
    :private-members:

.. autoclass:: Reporting
    :inherited-members:
    :members:

.. autoclass:: FileReporter
    :inherited-members:
    :members:

.. autoclass:: ClickReporter
    :inherited-members:
    :members:
    :private-members:

.. autoclass:: PathReporter
    :inherited-members:
    :members:
    :private-members:


GraphWalker
===========

.. module:: altwalker.graphwalker

.. currentmodule:: altwalker.graphwalker


REST Service
------------

For more informations check out the `GraphWalker REST API Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Rest-API-overview>`_.

.. autoclass:: GraphWalkerService
    :members:


.. autoclass:: GraphWalkerClient
    :members:


CLI
---

For more information check out the `GraphWalker CLI Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Command-Line-Tool>`_.

.. autofunction:: check

.. autofunction:: methods

.. autofunction:: offline


Model
=====

.. automodule:: altwalker.model

.. currentmodule:: altwalker.model

.. autofunction:: get_models

.. autofunction:: validate_json_models

.. autofunction:: validate_models

.. autofunction:: check_models


Code
====

.. automodule:: altwalker.code

.. currentmodule:: altwalker.code

.. autofunction:: get_methods

.. autofunction:: validate_code

.. autofunction:: verify_code


Exceptions
==========

.. module:: altwalker.exceptions

.. currentmodule:: altwalker.exceptions


Standard Exceptions
-------------------

.. autoexception:: GraphWalkerException
    :members:

.. autoexception:: AltWalkerException
    :members:

.. autoexception:: ValidationException
    :members:

.. autoexception:: ExecutorException
    :members:


Click Exceptions
----------------

This exceptions are used in the cli to handle the ``exit_code`` and the
display of :class:`GraphWalkerException` and :class:`AltWalkerException`.

.. autoexception:: FailedTestsError
    :members:

    .. autoattribute:: exit_code

.. autoexception:: GraphWalkerError
    :members:

    .. autoattribute:: exit_code

.. autoexception:: AltWalkerError
    :members:

    .. autoattribute:: exit_code
