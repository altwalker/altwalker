# AltWalker

AltWalker is an open source, Model-based testing framework for automating your test execution. You design your tests as a directional graph and AltWalker executes them. It relies on [Graphwalker](http://graphwalker.github.io/) to generate paths through your tests graph.

Read the documentation on https://altom.gitlab.io/altwalker/altwalker.

## Setup

Prerequisites:

* [Python3](https://www.python.org/) (with pip3)
* [Java 8](https://openjdk.java.net/)
* [GraphWalker CLI](http://graphwalker.github.io/)

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
