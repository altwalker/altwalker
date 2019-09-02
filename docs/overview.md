# Overview

__AltWalker__ is an open source, Model-Based Testing framework for automating your test execution. You design your tests as a directed graph and AltWalker executes them. It relies on [GraphWalker](http://graphwalker.github.io/) to generate paths through your graph.

## Model-Based Testing

[Model-Based Testing](https://en.wikipedia.org/wiki/Model-based_testing) is a testing
technique which offers a way of generating test cases based on models that describe the behaviour
(functionality) of the system under test.

The goal when designing models is to represent the part of the system under test, usually
by one model for each functionality of your system.

With the help of graph theory we can dynamically generate multiple test scripts. A test script is a path passing through the model from a starting point till
a condition is met.

__Why use Model-Based Testing__:

* the abstraction layer added by the model gives your tests a better structure
* the model can be updated to reflect the requirements changes making the tests easy to maintain
* dynamically generates multiple test scripts based on different conditions (like coverage or length)
* allows for a large number of tests to be created which results in a larger part of the system under test to be covered.

## AltWalker

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
    more about the Http Executor on the [How to: Write your own executor](https://altom.gitlab.io/altwalker/altwalker/how-tos/custom-executor.html)
    page.

* __Walker__: the test runner. Coordinates the execution of a test asking the `Planner`
    for the next step, executing the step using the `Executor` and reporting the progress
    using the `Reporter`.

There are two way to run your tests:

* __Online Mode__ (using the Online Planner): Generate one step and then execute
    the step, until the path is complete.

* __Offline Mode__ (using the Offline Planner): Run a path from a sequence of steps.
    Usually the path is generated using the `offline` command.

## GraphWalker

**GraphWalker** is an Model-Based Testing tool. It reads models in the
shape of directed graphs, and generate (test) paths from these graphs.

AltWalker uses [GraphWalker](http://graphwalker.github.io) as a Planner (it uses
the REST API as the Online Planner), so it inherits the model(s) formats
(graphml and json) and the generator and stop conditions.

AltWalker also uses the `offline`, `check` commands from GraphWalker.

The `offline` command form GraphWalker is used by the AltWalker's `offline` command, it takes
the output and saves it in a file as a list of step.

The `check` command from GraphWalker is used by AltWalker's `check`.

## Model-Editor

The [Model-Editor](https://altom.gitlab.io/altwalker/model-editor) is a web based editor
and visualizer for models written using the GraphWalker JSON format.

```eval_rst
.. figure:: _static/img/model-editor.png

    Screenshot taken from the Model-Editor.
```
