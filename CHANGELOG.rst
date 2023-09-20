Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Version 0.4.0
-------------

- The `init` command should generate a `.gitignore` file. (`#4`_)
- The `init` command should generate a `requirements.txt` file. (`#5`_)
- Drop support for python 3.5 and 3.6. (`#6`_)
- The `load_module` method is deprecated and will be removed in Python 3.12. (`#9`)
- Add the GraphWalker jar file as a resource file. (`#16`)
- The `pkg_resources` module is deprecated. (`#23`)
- Update the logging configuration to be more suited for a library. (`#24`)
- Remove the deprecated `-p`, `--port` and `--url` options. (`#26`)
- Drop support for python 3.7. (`#29`)
- Add `beforeStep` and `afterStep` fixtures. (`#33`)

.. _#4: https://github.com/altwalker/altwalker/issues/4
.. _#5: https://github.com/altwalker/altwalker/issues/5
.. _#6: https://github.com/altwalker/altwalker/issues/6
.. _#9: https://github.com/altwalker/altwalker/issues/9
.. _#16: https://github.com/altwalker/altwalker/issues/16
.. _#23: https://github.com/altwalker/altwalker/issues/23
.. _#24: https://github.com/altwalker/altwalker/issues/24
.. _#26: https://github.com/altwalker/altwalker/issues/26
.. _#29: https://github.com/altwalker/altwalker/issues/29
.. _#33: https://github.com/altwalker/altwalker/issues/33


Version 0.3.1
-------------

- Add a ``JUnitXMLReporter`` that will generate XML test reports that can be read by tools such as Jenkins or Bamboo. (`GitLab #150`_)
- Fix issue where the ``online`` command on Windows throws: *WinError 2 The system cannot find the specified*. (`GitLab #158`_)

.. _GitLab #150: https://gitlab.com/altom/altwalker/altwalker/issues/150
.. _GitLab #158: https://gitlab.com/altom/altwalker/altwalker/issues/158


Version 0.3.0
-------------

- Add requirements statistics from GraphWalker in report. (`GitLab #143`_)
- Add support for GraphWalker 4.3.0 and 4.3.1. (`GitLab #138`_, `GitLab #149`_)
- Add option for GraphWalker host for the ``online`` command. (`GitLab #126`_)
- Add support for edges without name. (`GitLab #125`_)
- Add option for GraphWalker log level. (`GitLab #119`_)
- Update the ``verify`` to output code suggestion for missing methods and classes. (`GitLab #101`_, `GitLab #106`_)
- Add an option to print the report path in a file. (`GitLab #108`_)
- Handel ``KeyboardInterrupt`` exception when executing tests to capture the method output. (`GitLab #107`_)
- Update CLI command output. (`GitLab #105`_, `GitLab #116`_, `GitLab #117`_, `GitLab #140`_)
- Fix issue where ``tearDownRun`` and ``tearDownModels`` do not run if a ``GraphWalkerException`` is raised. (`GitLab #110`_)
- Fix issue where ``Reporter.end`` is not call in case ``setUpRun`` fails. (`GitLab #109`_)
- Fix issue where he ``verify`` command doesn't work with paths ending with a path separator. (`GitLab #122`_)

.. _GitLab #101: https://gitlab.com/altom/altwalker/altwalker/issues/101
.. _GitLab #105: https://gitlab.com/altom/altwalker/altwalker/issues/105
.. _GitLab #106: https://gitlab.com/altom/altwalker/altwalker/issues/106
.. _GitLab #107: https://gitlab.com/altom/altwalker/altwalker/issues/107
.. _GitLab #108: https://gitlab.com/altom/altwalker/altwalker/issues/108
.. _GitLab #109: https://gitlab.com/altom/altwalker/altwalker/issues/109
.. _GitLab #110: https://gitlab.com/altom/altwalker/altwalker/issues/110
.. _GitLab #116: https://gitlab.com/altom/altwalker/altwalker/issues/116
.. _GitLab #117: https://gitlab.com/altom/altwalker/altwalker/issues/117
.. _GitLab #119: https://gitlab.com/altom/altwalker/altwalker/issues/119
.. _GitLab #122: https://gitlab.com/altom/altwalker/altwalker/issues/122
.. _GitLab #125: https://gitlab.com/altom/altwalker/altwalker/issues/125
.. _GitLab #126: https://gitlab.com/altom/altwalker/altwalker/issues/126
.. _GitLab #138: https://gitlab.com/altom/altwalker/altwalker/issues/138
.. _GitLab #140: https://gitlab.com/altom/altwalker/altwalker/issues/140
.. _GitLab #143: https://gitlab.com/altom/altwalker/altwalker/issues/143
.. _GitLab #149: https://gitlab.com/altom/altwalker/altwalker/issues/149


Version 0.2.7
-------------

(bugfix release)

- Update error messages for ``check``, ``offline`` and ``online`` commands. (`GitLab #102`_, `GitLab #103`_)
- Fix issue where ``sys.modules.__file__`` is optional and loading tests fails. (`GitLab #99`_)

.. _GitLab #99: https://gitlab.com/altom/altwalker/altwalker/issues/99
.. _GitLab #102: https://gitlab.com/altom/altwalker/altwalker/issues/102
.. _GitLab #103: https://gitlab.com/altom/altwalker/altwalker/issues/103


Version 0.2.6
-------------

(bugfix release)

- Fix issue where ``PythonExecutor`` doesn't work with decorated functions. (`GitLab #93`_)
- Unload previously loaded tests modules. (`GitLab #94`_)
- Update executeStep from HttpExecutor to post data dictionary inside the json ``data`` property. (`GitLab #96`_)
- Fix issue where the ``test.py`` module is executed twice. (`GitLab #98`_)

.. _GitLab #93: https://gitlab.com/altom/altwalker/altwalker/issues/93
.. _GitLab #94: https://gitlab.com/altom/altwalker/altwalker/issues/94
.. _GitLab #96: https://gitlab.com/altom/altwalker/altwalker/issues/96
.. _GitLab #98: https://gitlab.com/altom/altwalker/altwalker/issues/98


Version 0.2.5
-------------

(bugfix release)

- Add ``--log-level`` and ``--log-file`` options. (`GitLab #81`_)
- Pretty-print statistics for online. (`GitLab #84`_)
- Fix issue where the ``fail`` method from ``GraphWalkerClient`` throws an error. (`GitLab #80`_, `GitLab #85`_)

.. _GitLab #80: https://gitlab.com/altom/altwalker/altwalker/issues/80
.. _GitLab #81: https://gitlab.com/altom/altwalker/altwalker/issues/81
.. _GitLab #84: https://gitlab.com/altom/altwalker/altwalker/issues/84
.. _GitLab #85: https://gitlab.com/altom/altwalker/altwalker/issues/85


Version 0.2.4
-------------

(bugfix release)

- Fix issue where the graph data doesn't support boolean values. (`GitLab #75`_)
- Add an option to save the report to a file. (`GitLab #76`_)

.. _GitLab #75: https://gitlab.com/altom/altwalker/altwalker/issues/75
.. _GitLab #76: https://gitlab.com/altom/altwalker/altwalker/issues/76


Version 0.2.3
-------------

(bugfix release)

- Fix issue where the ``load`` method ``PythonExecutor`` it's not working. (`GitLab #66`_)
- Fix issue where ``generate`` commands deletes the content of the working directory. (`GitLab #67`_)
- Make git an optional dependency. (`GitLab #70`_)
- Don't let elements (e.g vertices, edges, ...) names to use python or C# keywords. (`GitLab #72`_)

.. _GitLab #66: https://gitlab.com/altom/altwalker/altwalker/issues/66
.. _GitLab #67: https://gitlab.com/altom/altwalker/altwalker/issues/67
.. _GitLab #70: https://gitlab.com/altom/altwalker/altwalker/issues/70
.. _GitLab #72: https://gitlab.com/altom/altwalker/altwalker/issues/72


Version 0.2.2
-------------

- Add ``--report-path`` flag, that if set will print a list of all executed steps.
- Make the ``Executor`` class an abstract class.
- Add a ``Reporting`` class that can combine multiple reporters.
- Add a ``PathReporter`` that keeps a list of all executed steps.
- Add ``host`` parameter to ``create_planner``.
- Update the reporter protocol. (`GitLab #53`_)
- Invalidate caches before loading module for python. (`GitLab #48`_)
- Fix issues where ``--start-element`` option doesn't pass the value to GraphWalker. (`GitLab #63`_)

.. _GitLab #63: https://gitlab.com/altom/altwalker/altwalker/issues/63
.. _GitLab #53: https://gitlab.com/altom/altwalker/altwalker/issues/53
.. _GitLab #48: https://gitlab.com/altom/altwalker/altwalker/issues/48


Version 0.2.1
-------------

(bugfix release)

- Fix issue with loading test code in python.


Version 0.2.0
-------------

- Add HTTP interface for the executor.
- Add C#/.NET executor.
- Fix issue where failed steps are not saved in statistics. (`GitLab #35`_)
- Fix issue where the ``init`` and ``generate`` commands outputs files with duplicate methods. (`GitLab #29`_)

.. _GitLab #35: https://gitlab.com/altom/altwalker/altwalker/issues/35
.. _GitLab #29: https://gitlab.com/altom/altwalker/altwalker/issues/29


Version 0.1.1
-------------

(bugfix release)

- Fix issue where output of a failed step is not reported. (`GitLab #20`_)

.. _GitLab #20: https://gitlab.com/altom/altwalker/altwalker/issues/20


Version 0.1.0
-------------

- Initial release.
