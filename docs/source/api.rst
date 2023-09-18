=================
API Documentation
=================

This section of the documentation provides a comprehensive API reference for
all public classes and functions.

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

* :class:`OnlinePlanner`: Uses GraphWalker online mode to generate the test
  path.

  With this method, the test code can directly interact with GraphWalker and
  modify the model data. A dictionary containing the model data is passed as
  the first argument to any method or function from the test code by
  the :class:`~altwalker.walker.Walker`` class.

* :class:`OfflinePlanner`: Uses a sequence of steps to generate the test path.

  The sequence of path can be generated using
  the :func:`~altwalker.graphwalker.offline` function.

.. autoclass:: Planner
    :members:

.. autoclass:: OnlinePlanner
    :members:

.. autoclass:: OfflinePlanner
    :members:

.. autofunction:: create_planner


Loader
======

.. module:: altwalker.loader

.. currentmodule:: altwalker.loader

.. autoclass:: ImportlibLoader

    .. automethod:: load

.. autoclass:: PrependLoader

    .. automethod:: load

.. autoclass:: AppendLoader

    .. automethod:: load

.. autoclass:: ImportModes

    .. autoattribute:: IMPORTLIB

    .. autoattribute:: PREPEND

    .. autoattribute:: APPEND


.. autofunction:: create_loader


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

.. autofunction:: create_executor


Reporter
========

.. module:: altwalker.reporter

.. currentmodule:: altwalker.reporter

The reporter plays a crucial role in capturing and presenting the results of a
test run. It's responsible for handling various events during the test
execution, and the following methods are called by the :class:`~altwalker.walker.Walker` class:

    * :func:`~Reporter.start`: Called at the beginning of each test run.
    * :func:`~Reporter.end`: Called at the end of each test run.
    * :func:`~Reporter.step_start`: Invoked before executing each step.
    * :func:`~Reporter.step_end`: Invoked after executing each step.
    * :func:`~Reporter.report`: This method should return report if the
      reporter generates one. For example, reporters like :class:`PrintReporter`
      or  :class:`FileReporter` might not generate reports but could log data.

It's important to note that the :func:`~Reporter.report` method is not called
by the :class:`~altwalker.walker.Walker` class; its purpose is to provide a
report when applicable.

To create a custom reporter, you should implement all of these methods. You can
inherit from the :class:`Reporter` class and override only the methods that you need to
customize. This allows you to tailor the reporter's behavior to your specific
requirements while maintaining consistency with the expected interface.


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

For more information check out the `GraphWalker REST API Documentation <https://github.com/GraphWalker/graphwalker-project/wiki/Rest-API-overview>`_.

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

These exceptions are employed in the CLI to manage the ``exit_code`` and
control the display of :class:`GraphWalkerException` and :class:`AltWalkerException`
exceptions.

.. autoexception:: FailedTestsError
    :members:

.. autoexception:: GraphWalkerError
    :members:

.. autoexception:: AltWalkerError
    :members:
