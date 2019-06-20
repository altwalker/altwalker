=================
API Documentation
=================

This part of the documentation lists the full API reference of all
public classes and functions.

.. module:: altwalker

Walker
------

.. module:: altwalker.walker

.. currentmodule:: altwalker.walker

.. autoclass:: Walker
    :members:

**Examples**:

You can run the tests using the :func:`Walker.run` method::

    walker = Walker(...)
    walker.run()

Or iterating over a :class:`Walker` object::

    walker = Walker(...)
    for step in walker:
        # do something with the step

.. autofunction:: create_walker


Planner
-------

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

        The sequense of path can be generated using
        the :func:`~altwalker.graphwalker.offline` function.

.. autoclass:: OnlinePlanner
    :members:

    .. automethod:: get_next

        Step example::

            {
                "id": step_id,
                "name": step_name,
                "modelName": model_name
            }

.. autoclass:: OfflinePlanner
    :members:

    Step example::

        {
            "name": step_name,
            "modelName": model_name
        }

.. autofunction:: create_planner


Executor
--------

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
--------

.. module:: altwalker.reporter

.. currentmodule:: altwalker.reporter

The role of the reporter is to report the results of a test run, a
reporter method is called by the :class:`~altwalker.walker.Walker`
for diffrent events:

    * :func:`~Reporter.start` - called at the beginning of each run.
    * :func:`~Reporter.end` - called at the end of each run.
    * :func:`~Reporter.step_start` - called before executing each step.
    * :func:`~Reporter.step_end` - called after executing each step.
    * :func:`~Reporter.report` - it should return a report if the reporter
      generates on (e.g. the :class:`PrintReporter` or
      :class:`FileReporter` don't generate any report, they only log data).
      It's not called by the :class:`~altwalker.walker.Walker`.

Every reporter should have all this methods, you can inherite them from
:class:`Reporter` and overwrite only the methods you want.

.. autoclass:: Reporter
    :members:
    :private-members:

.. autoclass:: Reporting
    :inherited-members:
    :members:

.. autoclass:: PrintReporter
    :inherited-members:
    :members:
    :private-members:

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
-----------

.. module:: altwalker.graphwalker

.. currentmodule:: altwalker.graphwalker


REST Service
~~~~~~~~~~~~

For more informations check out the `GraphWalker REST API Documentation <http://graphwalker.github.io/rest-overview/>`_.

.. autoclass:: GraphWalkerService
    :members:

    .. automethod:: __init__


.. autoclass:: GraphWalkerClient
    :members:

    .. automethod:: __init__

    .. automethod:: get_next

        Depending of how the GraphWalker Service was started ``get_next`` will return different responses.

        With the verbose flag::

            {
                "id": step_id,
                "name": step_name,
                "modelName": model_name,
                "data": [],
                "properties": {}
            }

        With the unvisited flag::

            {
                "id": step_id,
                "name": step_name,
                "modelName": model_name,
                "numberOfElements": number_of_element,
                "numberOfUnvisitedElements": number_of_unvisted_elements,
                "unvisitedElements": []
            }

CLI
~~~

For more informations check out the `GraphWalker CLI Documentation <http://graphwalker.github.io/cli-overview/>`_.

.. autofunction:: check

.. autofunction:: methods

.. autofunction:: offline


Models
------

.. automodule:: altwalker.model

.. currentmodule:: altwalker.model


.. autofunction:: validate_model

.. autofunction:: validate_models

.. autofunction:: check_models

.. autofunction:: get_methods

.. autofunction:: validate_code

.. autofunction:: verify_code

.. autofunction:: get_models


Exceptions
----------

.. module:: altwalker.exceptions

.. currentmodule:: altwalker.exceptions


Standard Exceptions
~~~~~~~~~~~~~~~~~~~

.. autoexception:: GraphWalkerException
    :members:

.. autoexception:: AltWalkerException
    :members:

.. autoexception:: ValidationException
    :members:

.. autoexception:: ExecutorException
    :members:


Click Exceptions
~~~~~~~~~~~~~~~~

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
