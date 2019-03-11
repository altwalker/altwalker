# AltWalker

AltWalker is an open source, Model-based testing framework for automating your test execution. You
design your tests as a directional graph and AltWalker executes them. It relies on
[Graphwalker](http://graphwalker.github.io/) to generate paths through your tests graph.

Read the documentation on https://altom.gitlab.io/altwalker/altwalker.

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
  chmod 777 ~/graphwalker/graphwalker-cli.sh && \
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
$ altwalker init test-project
$ cd test-project
$ altwalker online tests -m models/default.json "ramndom(vertex_coverage(100))"
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
  pip3 install -r requrements-dev.txt
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
open _build/html/index.html
```
