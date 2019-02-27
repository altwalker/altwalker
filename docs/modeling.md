# Modeling

## Model design

The objective of the model, is to express the expected behavior of the system under test. To do so, we use a directed graph, in which a vertex (or a node) represents some desired state, and the edges (arcs, arrows, transitions) represents whatever actions we need to do in order to achieve that desired state.

Graphwalker generates a path through the directed graph. Altwalker walks the path and executes the code associated to the reached vertex or edge. Each vertex and edge has an associated method in code that is executed upon stepping into it.

For a deeper dive into model design check [Graphwalker -> Documentation -> The ruleset of modeling](http://graphwalker.github.io/yed_model_syntax/).

## Tooling

For creating or modifying json model you can use [Altwalker model editor](https://altom.gitlab.io/altwalker/model-editor).

For creating or modifying graphml models you can use [yEd editor](http://www.yworks.com/en/products_yed_about.html).

## Json model format

For documentation about json model format check [Graphwalker -> File formats](http://graphwalker.github.io/json-overview/).