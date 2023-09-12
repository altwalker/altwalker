# AltWalker

AltWalker is an open source, Model-Based Testing framework.

Read the documentation on https://altwalker.github.io/altwalker.

Join our [Gitter chat room](https://gitter.im/altwalker/community) or our [Google Group](https://groups.google.com/g/altwalker) to chat with us or with other members of the community.

## Table of Contents

* [Overview](#overview)
* [Installation](#installation)
* [Quickstart](#quickstart)
* [Setting Up a Development Environment](#setting-up-a-development-environment)
* [Support](#support)
* [License](#license)

## Overview

*AltWalker* is an open source Model-Based Testing framework that supports running
tests written in python3 and .NET/C#. You design your tests as a directed graph
and AltWalker generates test cases from your graph (using [GraphWalker](http://graphwalker.github.io/)) and executes them.

### Model-Based Testing

[Model-Based Testing](https://en.wikipedia.org/wiki/Model-based_testing) is a testing
technique which offers a way of generating test cases based on models that describe the behavior
(functionality) of the system under test.

The goal when designing models is to represent the part of the system under test, usually
by one model for each functionality of your system.

With the help of graph theory we can dynamically generate multiple test scripts. A test script is a path passing through the model from a starting point till
a condition is met.

Why use Model-Based Testing:

* the abstraction layer added by the model gives your tests a better structure
* the model can be updated to reflect the requirements changes making the tests easy to maintain
* dynamically generates multiple test scripts based on different conditions (like coverage or length)
* allows for a large number of tests to be created which results in a larger part of the system under test to be covered.

### AltWalker

AltWalker is a test execution tool, which  aims to make it easy to write and run your model-based tests. AltWalker uses GraphWalker to generate a path through the models.

For the test structure it uses an Object-Oriented approach inspired by python's `unittest` module. Every model is mapped to a class with the same name and each vertex and edge from the model is mapped to a method inside the class.

AltWalker also borrows the concept of test fixture from unit tests, and implements the following fixtures:
`setUpRun`, `tearDownRun`, `setUpModel` and `tearDownModel`.

Now it supports running tests written in .NET/C# and Python3.

### AltWalker Components

AltWalker has the following components:

* __Model__: a directed graph, supplied by the user as a json or graphml file.
    A graph is composed from a list of vertices and a list of edges.

* __Generator__ and __Stop Condition__: used to specify how to generate a
    path and to decide when a path is complete.

* __Test Code__: the implementation of the model(s) as code. Each model is mapped to a
    class and each vertex and edge is mapped to a method.

* __Planner__: uses the _model(s)_ and a pair of _generator_ and _stop condition_
    to provide a path (a sequence of steps) through the model(s).

    Currently AltWalker provides two planners:

    * Online Planner
    * Offline Planner

* __Reporter__: reports the output of the tests, the reporter is called on
    each event (e.g. `step_start`, `step_end`, ...).

* __Executor__: for each step in the plan it looks up and calls the named method
    from the _test code_. In addition to the step methods, it also calls
    fixture methods if present (e.g. `setUpModel`, `tearDownModel` ...).

    Currently AltWalker provides three executors:

    * Python Executor
    * .NET Executor

    And an __Http Executor__ that allows you to hook up your own executor via HTTP. You can read
    more about the Http Executor on the [How to: Write your own executor](https://altwalker.github.io/altwalker/advanced-usage/custom-executor.html)
    page.

* __Walker__: the test runner. Coordinates the execution of a test asking the `Planner`
    for the next step, executing the step using the `Executor` and reporting the progress
    using the `Reporter`.


There are two ways to run your tests:

* __Online Mode__ (using the Online Planner): Generate one step and then execute
    the step, until the path is complete.

* __Offline Mode__ (using the Offline Planner): Run a path from a sequence of steps.
    Usually the path is generated using the `offline` command.

## Installation

Prerequisites:

* [Python3](https://www.python.org/) (with pip3)
* [Java 8](https://openjdk.java.net/)
* [GraphWalker CLI](http://graphwalker.github.io/) (Optional)
* [.NET Core](Optional) (Optional)
* [git](https://git-scm.com/) (Optional)

### Install AltWalker

To install ``altwalker`` run the following command in your command line:

```
$ pip install altwalker
```

To check that you have installed the correct version of AltWalker, run the
following command:

```
$ altwalker --version
```

#### Living on the edge

If you want to work with the latest code before it’s released, install or update the code from the `develop` branch:

```
$ pip install -U git+https://github.com/altwalker/altwalker
```

For a more detailed tutorial read the [Installation](https://altwalker.github.io/altwalker/installation.html) section from the documentation.

## Quickstart

Make a sample project and run the tests.

```
$ altwalker init test-project -l python
$ cd test-project
$ altwalker online tests -m models/default.json "random(vertex_coverage(100))"
Running:
[2019-08-06 16:28:44.030077] ModelName.vertex_A Running
[2019-08-06 16:28:44.030940] ModelName.vertex_A Status: PASSED

[2019-08-06 16:28:44.048492] ModelName.edge_A Running
[2019-08-06 16:28:44.048729] ModelName.edge_A Status: PASSED

[2019-08-06 16:28:44.064495] ModelName.vertex_B Running
[2019-08-06 16:28:44.064746] ModelName.vertex_B Status: PASSED

Statistics:

  Model Coverage..................100%
  Number of Models...................1
  Completed Models...................1
  Failed Models......................0
  Incomplete Models..................0
  Not Executed Models................0

  Edge Coverage...................100%
  Number of Edges....................1
  Visited Edges......................1
  Unvisited Edges....................0

  Vertex Coverage.................100%
  Number of Vertices.................2
  Visited Vertices...................2
  Unvisited Vertices.................0

Status:  PASS
```

## Setting Up a Development Environment

Clone the repository:

```
$ git clone https://github.com/altwalker/altwalker.git
$ cd altwalker
```

Install python dependencies:

```
$ pip install -r requirements.txt && \
  pip install -r requirements-dev.txt
```

### Running Tests

```
$ pytest tests -s -v
```

#### Running tests with tox inside Docker

```
$ docker run  -it --rm -v "$(pwd):/altwalker" -w "/altwalker" altwalker/tests:tox tox
```

### CLI

After you install the python dependencies to setup AltWalker CLI locally from code run:

```
$ pip install --editable .
```

Then from any command line you can access:

```
$ altwalker --help
```

### Documentation

After you install the python dependencies to generate the documentation run:

```
$ cd docs && \
  make clean && \
  make html
```

To see the documentation run:

```
$ open build/html/index.html
```

To rebuild the documentation on changes, with live-reload in the browser run:

```
$ sphinx-autobuild docs/source docs/build/html
```

Navigate to the documentation at http://127.0.0.1:8000.


__Further Reading/Useful Links__:

* [Google Style Docstring Example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html#example-google)
* [Google Style Guide](https://google.github.io/styleguide/pyguide.html)

## Support

Join our [Gitter chat room](https://gitter.im/altwalker/community) or our [Google Group](https://groups.google.com/g/altwalker) to chat with us or with other members of the community.

## License

This project is licensed under the [GNU General Public License v3.0](https://github.com/altwalker/altwalker/blob/main/LICENSE).
