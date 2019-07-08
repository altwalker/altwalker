# Overview

AltWalker is an open source, Model-Based testing framework for automating your
test execution. You design your tests as a directional graph and AltWalker
executes them. It relies on GraphWalker to generate paths through your
tests graph.

## Model-Based Testing

[Model-Based Testing](https://en.wikipedia.org/wiki/Model-based_testing) is a testing
technique which offers a way of generating tests cases based on models, models
that describe the behaviour (functionality) of the system under test.

The role of the model is to describe the system under tests. The goal when designing
models is to represent the part of the system you want to test, usually you will
design one model for each functionality of your system.

## AltWalker

AltWalker has the following components:

- **Model**: a directed graph, supplied by the user as a json or graphml file.
  A graph is composed from a list of vertices and a list of edges.

- **Generator** and **Stop Condition**: used to specify how to generate a
  path and to decide when a path is complete.

- **Test Code**: The implementation of the model(s) as code. Each vertex and edge
  is mapped to a method from the test code.

- **Planner**: Which uses the _model(s)_ and a pair of _generator_ and _stop condition_
  to provide a path (a sequence of steps) through the model(s).

  Currently AltWalker provides two planner:

  - Online Planner
  - Offline Planner

- **Reporter**: To report the results of the tests, the reporters are all called for
  each event (e.g. `step_start`, `step_end`, ...).

- **Executor**: For each step in the plan looks up and calls the named method
  from the _test code_. In addition to the step methods, it also calls
  fixture methods if present (e.g. `setUpModel`, `tearDownModel` ...).

  Currently AltWalker provides two executors:

  - Python Executor
  - .NET Executor

  And an **Http Executor** that allows you to hook up your own executor via HTTP. You can read
  more about the Http Executor on the [How to: Write your own executor](./how-tos/custom-executor)
  page.

- **Walker**: The test runner. Coordinates the execution of a test asking a `Planner`
  for the next step, executing the step using an `Executor` and reporting the progress
  using a `Reporter`.

There are two ways to run your test:

- **Online Mode** (with the Online Planner): Generate one step and then execute
  the step, until the path is complete.

- **Offline Mode** (with the Offline Planner): Run a path from a sequence of steps.
  Usually the path is generated using the `offline` command.

## GraphWalker

**GraphWalker**: is an Model-Based testing tool. It reads models in the
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
