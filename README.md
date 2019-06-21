# AltWalker

AltWalker is an open source, Model-based testing framework for automating your test execution. You
design your tests as a directional graph and AltWalker executes them. It relies on
[Graphwalker](http://graphwalker.github.io/) to generate paths through your tests graph.

Read the documentation on https://altom.gitlab.io/altwalker/altwalker.

## Model-Based Testing

[Model-Based Testing](https://en.wikipedia.org/wiki/Model-based_testing) is a testing
technique which offers a way of generating tests cases based on models, models
that describe the behaviour (functionality) of the system under test.

The role of the model is to describe the system under tests. The goal when designing
models is to represent the part of the system you want to test, usually you will
design one model for each functionality of your system.

## AltWalker

AltWalker has the following components:

* __Model__: a directed graph, supplied by the user as a json or graphml file.
    A graph is composed from a list of vertices and a list of edges.

* __Generator__ and __Stop Condition__: used to specify how to generate a
    path and to decide when a path is complete.

* __Test Code__: The implementation of the model(s) as code. Each vertex and edge
    is mapped to a method from the test code.

* __Planner__: Which uses the _model(s)_ and a pair of _generator_ and _stop condition_
    to provide a path (a sequence of steps) through the model(s).

    Currently AltWalker provides two planner:

    * Online Planner
    * Offline Planner

* __Reporter__: To report the results of the tests, the reporters are all called for
    each event (e.g. `step_start`, `step_end`, ...).

* __Executor__: For each step in the plan looks up and calls the named method
    from the _test code_. In addition to the step methods, it also calls
    fixture methods if present (e.g. `setUpModel`, `tearDownModel` ...).

    Currently AltWalker provides three executors:

    * Python Executor
    * .NET Executor

    And an __Http Executor__ that allows you to hook up your own executor via HTTP. You can read
    more about the Http Executor on the [How to: Write your own executor](https://altom.gitlab.io/altwalker/altwalker/how-tos/custom-executor.html)
    page.

* __Walker__: The test runner. Coordinates the execution of a test asking a `Planner`
    for the next step, executing the step using an `Executor` and reporting the progress
    using a `Reporter`.


There are two way to run your test:

* __Online Mode__ (with the Online Planner): Generate one step and then execute
    the step, until the path is complete.

* __Offline Mode__ (with the Offline Planner): Run a path from a sequence of steps.
    Usually the path is generated using the `offline` command.

## Install

Prerequisites:

* [Python3](https://www.python.org/) (with pip3)
* [Java 8](https://openjdk.java.net/)
* [GraphWalker CLI](http://graphwalker.github.io/)

Install GraphWalker:

* MacOS/Linux:

```bash
$ wget https://github.com/GraphWalker/graphwalker-project/releases/download/LATEST-BUILDS/graphwalker-cli-4.0.0-SNAPSHOT.jar && \
  mkdir -p ~/graphwalker && \
  mv graphwalker-cli-4.0.0-SNAPSHOT.jar ~/graphwalker/ && \
  echo -e '#!/bin/bash\njava -jar ~/graphwalker/graphwalker-cli-4.0.0-SNAPSHOT.jar "$@"' > ~/graphwalker/graphwalker-cli.sh && \
  chmod +x ~/graphwalker/graphwalker-cli.sh && \
  ln -s ~/graphwalker/graphwalker-cli.sh /usr/local/bin/gw
```

* Windows:

```
$ setx PATH "%PATH%;C:\graphwalker" & :: Adds graphwalker to current user PATH
  cd C:\
  mkdir graphwalker
  cd graphwalker
  powershell -Command "[Net.ServicePointManager]::SecurityProtocol = 'tls12'; Invoke-WebRequest -Uri 'https://github.com/GraphWalker/graphwalker-project/releases/download/LATEST-BUILDS/graphwalker-cli-4.0.0-SNAPSHOT.jar' -outfile 'graphwalker-cli-4.0.0-SNAPSHOT.jar'" & :: Downloads graphwalker using powershell command Invoke-Request
  @echo off
  @echo @echo off> gw.bat
  @echo java -jar C:\graphwalker\graphwalker-cli-4.0.0-SNAPSHOT.jar %*>> gw.bat
  @echo on
```

After running the command check that you correctly installed GraphWalker by running:

```
$ gw --version
```

Install AltWalker:

```
$ pip3 install altwalker
$ altwalker --version
```

For a more detailed tutorial read the [Installation](https://altom.gitlab.io/altwalker/altwalker/installation.html) section from the documentation.

## Quickstart

Make a sample project and run the tests.

```
$ altwalker init test-project -l python
$ cd test-project
$ altwalker online tests -m models/default.json "random(vertex_coverage(100))"
Running:
[2019-02-28 11:49:21.803956] ModelName.vertex_A Running
[2019-02-28 11:49:21.804709] ModelName.vertex_A Status: PASSED
[2019-02-28 11:49:21.821219] ModelName.edge_A Running
[2019-02-28 11:49:21.821443] ModelName.edge_A Status: PASSED
[2019-02-28 11:49:21.836176] ModelName.vertex_B Running
[2019-02-28 11:49:21.836449] ModelName.vertex_B Status: PASSED
Statistics:
{
    "edgeCoverage": 100,
    "edgesNotVisited": [],
    "failedFixtures": [],
    "failedStep": {},
    "steps": [
        {
            "id": "v0",
            "modelName": "ModelName",
            "name": "vertex_A"
        },
        {
            "id": "e0",
            "modelName": "ModelName",
            "name": "edge_A"
        },
        {
            "id": "v1",
            "modelName": "ModelName",
            "name": "vertex_B"
        }
    ],
    "totalCompletedNumberOfModels": 1,
    "totalFailedNumberOfModels": 0,
    "totalIncompleteNumberOfModels": 0,
    "totalNotExecutedNumberOfModels": 0,
    "totalNumberOfEdges": 1,
    "totalNumberOfModels": 1,
    "totalNumberOfUnvisitedEdges": 0,
    "totalNumberOfUnvisitedVertices": 0,
    "totalNumberOfVertices": 2,
    "totalNumberOfVisitedEdges": 1,
    "totalNumberOfVisitedVertices": 2,
    "vertexCoverage": 100,
    "verticesNotVisited": []
}
Status: True
```

## Setting Up a Development Environment

### Running Tests

Install python dependencies:

```
$ pip3 install -r requirements.txt && \
  pip3 install -r requirements-dev.txt
```

Run tests:

```
$ pytest tests -s -v
```

### CLI

After you install the python dependencies to setup AltWalker CLI locally from code run:

```
$ pip3 install --editable .
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
$ open _build/html/index.html
```

__Further Reading/Useful Links__:

* [Google Style Docstring Example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html#example-google)
* [Google Style Guide](https://google.github.io/styleguide/pyguide.html)
