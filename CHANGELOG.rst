Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


Version 0.3.1
-------------

- Add a ``JUnitXMLReporter`` that will generate XML test reports that can be read by tools such as Jenkins or Bamboo. (`#150`_)
- Fix issue where the ``online`` command on Windows throws: *WinError 2 The system cannot find the specified*. (`#158`_)

.. _#150: https://gitlab.com/altom/altwalker/altwalker/issues/150
.. _#158: https://gitlab.com/altom/altwalker/altwalker/issues/158


Version 0.3.0
-------------

- Add requirements statistics from GraphWalker in report. (`#143`_)
- Add support for GraphWalker 4.3.0 and 4.3.1. (`#138`_, `#149`_)
- Add option for GraphWalker host for the ``online`` command. (`#126`_)
- Add support for edges without name. (`#125`_)
- Add option for GraphWalker log level. (`#119`_)
- Update the ``verify`` to output code suggestion for missing methods and classes. (`#101`_, `#106`_)
- Add an option to print the report path in a file. (`#108`_)
- Handel ``KeyboardInterrupt`` exception when executing tests to capture the method output. (`#107`_)
- Update CLI command output. (`#105`_, `#116`_, `#117`_, `#140`_)
- Fix issue where ``tearDownRun`` and ``tearDownModels`` do not run if a ``GraphWalkerException`` is raised. (`#110`_)
- Fix issue where ``Reporter.end`` is not call in case ``setUpRun`` fails. (`#109`_)
- Fix issue where he ``verify`` command doesn't work with paths ending with a path separator. (`#122`_)

.. _#101: https://gitlab.com/altom/altwalker/altwalker/issues/101
.. _#105: https://gitlab.com/altom/altwalker/altwalker/issues/105
.. _#106: https://gitlab.com/altom/altwalker/altwalker/issues/106
.. _#107: https://gitlab.com/altom/altwalker/altwalker/issues/107
.. _#108: https://gitlab.com/altom/altwalker/altwalker/issues/108
.. _#109: https://gitlab.com/altom/altwalker/altwalker/issues/109
.. _#110: https://gitlab.com/altom/altwalker/altwalker/issues/110
.. _#116: https://gitlab.com/altom/altwalker/altwalker/issues/116
.. _#117: https://gitlab.com/altom/altwalker/altwalker/issues/117
.. _#119: https://gitlab.com/altom/altwalker/altwalker/issues/119
.. _#122: https://gitlab.com/altom/altwalker/altwalker/issues/122
.. _#125: https://gitlab.com/altom/altwalker/altwalker/issues/125
.. _#126: https://gitlab.com/altom/altwalker/altwalker/issues/126
.. _#138: https://gitlab.com/altom/altwalker/altwalker/issues/138
.. _#140: https://gitlab.com/altom/altwalker/altwalker/issues/140
.. _#143: https://gitlab.com/altom/altwalker/altwalker/issues/143
.. _#149: https://gitlab.com/altom/altwalker/altwalker/issues/149


Version 0.2.7
-------------

(bugfix release)

- Update error messages for ``check``, ``offline`` and ``online`` commands. (`#102`_, `#103`_)
- Fix issue where ``sys.modules.__file__`` is optional and loading tests fails. (`#99`_)

.. _#99: https://gitlab.com/altom/altwalker/altwalker/issues/99
.. _#102: https://gitlab.com/altom/altwalker/altwalker/issues/102
.. _#103: https://gitlab.com/altom/altwalker/altwalker/issues/103


Version 0.2.6
-------------

(bugfix release)

- Fix issue where ``PythonExecutor`` doesn't work with decorated functions. (`#93`_)
- Unload previously loaded tests modules. (`#94`_)
- Update executeStep from HttpExecutor to post data dictionary inside the json ``data`` property. (`#96`_)
- Fix issue where the ``test.py`` module is executed twice. (`#98`_)

.. _#93: https://gitlab.com/altom/altwalker/altwalker/issues/93
.. _#94: https://gitlab.com/altom/altwalker/altwalker/issues/94
.. _#96: https://gitlab.com/altom/altwalker/altwalker/issues/96
.. _#98: https://gitlab.com/altom/altwalker/altwalker/issues/98


Version 0.2.5
-------------

(bugfix release)

- Add ``--log-level`` and ``--log-file`` options. (`#81`_)
- Pretty-print statistics for online. (`#84`_)
- Fix issue where the ``fail`` method from ``GraphWalkerClient`` throws an error. (`#80`_, `#85`_)

.. _#80: https://gitlab.com/altom/altwalker/altwalker/issues/80
.. _#81: https://gitlab.com/altom/altwalker/altwalker/issues/81
.. _#84: https://gitlab.com/altom/altwalker/altwalker/issues/84
.. _#85: https://gitlab.com/altom/altwalker/altwalker/issues/85


Version 0.2.4
-------------

(bugfix release)

- Fix issue where the graph data doesn't support boolean values. (`#75`_)
- Add an option to save the report to a file. (`#76`_)

.. _#75: https://gitlab.com/altom/altwalker/altwalker/issues/75
.. _#76: https://gitlab.com/altom/altwalker/altwalker/issues/76


Version 0.2.3
-------------

(bugfix release)

- Fix issue where the ``load`` method ``PythonExecutor`` it's not working. (`#66`_)
- Fix issue where ``generate`` commands deletes the content of the working directory. (`#67`_)
- Make git an optional dependency. (`#70`_)
- Don't let elements (e.g vertices, edges, ...) names to use python or C# keywords. (`#72`_)

.. _#66: https://gitlab.com/altom/altwalker/altwalker/issues/66
.. _#67: https://gitlab.com/altom/altwalker/altwalker/issues/67
.. _#70: https://gitlab.com/altom/altwalker/altwalker/issues/70
.. _#72: https://gitlab.com/altom/altwalker/altwalker/issues/72


Version 0.2.2
-------------

- Add ``--report-path`` flag, that if set will print a list of all executed steps.
- Make the ``Executor`` class an abstract class.
- Add a ``Reporting`` class that can combine multiple reporters.
- Add a ``PathReporter`` that keeps a list of all executed steps.
- Add ``host`` parameter to ``create_planner``.
- Update the reporter protocol. (`#53`_)
- Invalidate caches before loading module for python. (`#48`_)
- Fix issues where ``--start-element`` option doesn't pass the value to GraphWalker. (`#63`_)

.. _#63: https://gitlab.com/altom/altwalker/altwalker/issues/63
.. _#53: https://gitlab.com/altom/altwalker/altwalker/issues/53
.. _#48: https://gitlab.com/altom/altwalker/altwalker/issues/48


Version 0.2.1
-------------

(bugfix release)

- Fix issue with loading test code in python.


Version 0.2.0
-------------

- Add HTTP interface for the executor.
- Add C#/.NET executor.
- Fix issue where failed steps are not saved in statistics. (`#35`_)
- Fix issue where the ``init`` and ``generate`` commands outputs files with duplicate methods. (`#29`_)

.. _#35: https://gitlab.com/altom/altwalker/altwalker/issues/35
.. _#29: https://gitlab.com/altom/altwalker/altwalker/issues/29


Version 0.1.1
-------------

(bugfix release)

- Fix issue where output of a failed step is not reported. (`#20`_)

.. _#20: https://gitlab.com/altom/altwalker/altwalker/issues/20


Version 0.1.0
-------------

- Initial release.