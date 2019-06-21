# Modeling

```eval_rst
.. contents:: Table of Contents
    :local:
    :backlinks: none
```

## Model Design

The objective of the model(s), is to express the expected behaviour of the system under test. To do so, we use a directed graph, in which a vertex (or a node) represents some desired state, and the edges (arcs, arrows, transitions) represents whatever actions we need to do in order to achieve that desired state.

Each vertex and edge has an associated method in the test code that is executed upon stepping into it.

_GraphWalker_ generates a path through the directed graph. _AltWalker_ walks the path and executes the code associated to the reached vertex or edge.

### Vertices

A __vertex__ is a state of the system under tests. In the test code this is the place where the actual test takes place.

### Edges

A __edge__ is an action that takes the system under tests form one state (vertex) to another.

### Generators and Stop Conditions

__Generators__ and __stop conditions__ are how GraphWalker decides how to travel the model(s) (directed graph) and when the path (test sequence) is completed.

A __generator__ is an algorithm that decides how to traverse a model. Different generators will generate different test sequences, and they will navigate in different ways.

A __stop condition__ is condition that decides when a path is completed. The __generator__ will generate a new step in the path until the __stop condition__ is fulfilled.

Generators:
  * `random(<stop_conditions>)`
  * `weighted_random(<stop_conditions>)`
  * `quick_random(<stop_conditions>)`
  * `a_star(<stop_conditions>)`

Stop Conditions:
  * `edge_coverage(<percentage>)`
  * `vertex_coverage(<percentage>)`
  * `requirement_coverage(<percentage>)`
  * `dependency_edge_coverage(<percentage>)`
  * `reached_vertex(<vertex_name>)`
  * `reached_edge(<edge_name>)`
  * `time_duration(<number_of_seconds>)`
  * `length(<integer>)`
  * `never`


__Examples__:

```
random(never)
```

```
weighted_random(time_duration(100))
```

```
a_start(reached_vertex(vertex_A))
```

```eval_rst
.. note::
    Throughout the documentation a pair of a generator and a stop condition is usually referred as a stop condition.
```

__Further Reading/Useful Links__:
  * For documentation about Generators and Stop Conditions check [GraphWalker's documentation](http://graphwalker.github.io/generators_and_stop_conditions/)

### Actions

GraphWalker keeps an execution context with data for each model and a global context.

By default GraphWalker tried to access data from the current model context, to access data from the global context prefix the variable name with `global.` (e.g. `global.count`, `global.isLoggedIn`).

An __action__ is a piece of java code that you want the model to execute, in order to modify the data from the context.

Actions can only be placed on edges or models.

```eval_rst
.. tip::
  Always initialize your variables in the models level actions.

  Note that you can also initialize variables in the global context.
```

__Example__:

```json
{
    "actions": [
        "numOfPets++;",
        "isLoggedIn = true;"
    ]
}
```

And to update variable from the global context:

```json
{
    "actions": [
        "global.numOfPets++;",
    ]
}
```


```eval_rst
.. note::
  Each action must end with ``;`` (e.g. ``count++;``, ``isLoggedIn = true;``).
```

__Further Reading/Useful Links__:
  * Read more on actions and guards in the [How to: Use actions and guards](how-tos/actions-and-guards) section.

### Guards

A __guard__ is a condition that until is fulfilled marks a __edge__ as unreachable, the __guard__ is expressed using the data from the context.

Guards can only be placed on edges.

__Example__:

```json
{
    "guard": "numOfPets > 0"
}
```

Like with __actions__ if you want to use data form the global context prefix the variable name with `global.`.

```json
{
    "guard": "global.numOfPets > 0"
}
```

__Further Reading/Useful Links__:
  * Read more on actions and guards in the [How to: Use actions and guards](how-tos/actions-and-guards) section.

## Formats

AltWalker like GraphWalker supports two formats for models:

* json
* grapml

### JSON

The template for a __json__ file.

```json
{
  "name": "<Name of the test suite>",
  "models": [
    {
      "<MODEL IN JSON FORMAT>"
    },
    {
      "<MODEL IN JSON FORMAT>"
    }
  ]
}
```

Multiple models and their data can be stored in one single json file.

The template for a __model__:

```json
{
    "generator": "<The generator of the model>",
    "id": "<The unique id of the model>",
    "name": "<The name of the model>",
    "actions": [
        "<ACTION IN JSON FORMAT>",
        "<ACTION IN JSON FORMAT>"
    ],
    "edges": [
        "<EDGE IN JSON FORMAT>",
        "<EDGE IN JSON FORMAT>"
    ],
    "vertices": [
        "<VERTEX IN JSON FORMAT>",
        "<VERTEX IN JSON FORMAT>"
    ]
}
```

* `action` field is optional.

The template for a __vertex__:

```json
{
    "id": "<The unique id of the vertex>",
    "name": "<The name of the vertex>",
    "properties": {
        "key1": "<value1>",
        "key2": "<value2>"
    },
    "sharedState": "<SHARED STATE NAME>"
}
```

* `properties` field is optional, it can be used to store pairs of key/data.
* `sharedState` field is optional, it can be used to link to vertices from different models.

    Any vertices with the same value for `sharedState` are linked.

The template for an __edge__:

```json
{
    "id": "<The unique id of the edge>",
    "name": "<The name of the edge>",
    "sourceVertexId": "<The id of the source vertex of this edge>",
    "targetVertexId": "<The id of the target, or destination vertex of this edge>",
    "guard": "<The conditional expression which enables the accessibility of this edge>",
    "actions": [
        "<ACTION IN JSON FORMAT>",
        "<ACTION IN JSON FORMAT>"
    ],
}
```

* `guard` field is optional, it can be used to set a guard on this edge.
* `action` field is optional.

The template for an __action__:

```json
{
    "actions": [
        "<JAVA SCRIPT;>",
        "<JAVA SCRIPT;>"
    ]
}
```

Is a piece of java code that you want the model to execute.

It has to end with a semi colon.


__Further Reading/Useful Links__:
  * For documentation about __json__ format check [GraphWalker documentation](http://graphwalker.github.io/json-overview/).
  * For creating or modifying json models you can use [AltWalker's model editor](https://altom.gitlab.io/altwalker/model-editor).

### GraphML

[GraphML](https://en.wikipedia.org/wiki/GraphML) is an XML-based file format for graphs.

A single model and his data can be stored in one single `.graphml` file. The name of the model is the name of the file (e.g. for `login.graphml` the name of the model is `login`).

```eval_rst
.. admonition:: Recommendation

  If you intent to use the ``graphml`` format we recomand considering using the ``json`` format. AltWalker is mainly tested using ``json`` models and all the example from the
  documentation use the ``json`` format.

  If you have models in the ``graphl`` format we recomand converting them using the `convert <http://graphwalker.github.io/cli-convert/#version-4>`_ command form GraphWalker.

  **Example**:

  .. code-block:: console

    $ gw convert -i login.graphml -f json

```

__Further Reading / Useful Links__:
  * [GraphML](https://en.wikipedia.org/wiki/GraphML) file format.
  * For documentation about `.graphml` model format check [GraphWalker's documentation](http://graphwalker.github.io/yed_model_syntax/).
  * For creating or modifying graphml models you can use [yEd editor](http://www.yworks.com/en/products_yed_about.html).

## Tooling

For __json__ you can check [AltWalker's Model-Editor](https://altom.gitlab.io/altwalker/model-editor), the editor allows you to visualize the model while you are working on it.

For __GraphML__ you can use [yEd editor](http://www.yworks.com/en/products_yed_about.html) and GraphWalker has a tutorial on how to [design models](http://graphwalker.github.io/yed_model_syntax/) using it.

You can also check for issues in the model(s) using the `check` command:

```
$ altwalker check -m path/to/model.json
```

```
$ altwalker check -m path/to/model.graphml
```
