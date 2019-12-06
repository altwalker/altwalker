Path Generation
===============

AltWalker relies on GraphWalker to generate paths through your graph.

Path generation consists of two parts: *"how to cover?"* (generators) and
*"what to cover?"* (stop conditions).

GraphWalker uses **generators** and **stop conditions** to decide how to
walk through the model(s) (directed graph) and when the path (test sequence) is
completed.

.. contents:: Table of Contents
    :local:


Generators
----------

A **generator** is an algorithm that decides how to traverse a model. Different
generators will generate different test sequences, and they will navigate in
different ways.

Random
~~~~~~

Navigate through the models in a completely random manner, also called
**random walk**. This algorithm selects randomly an out-edge from a vertex,
and repeats the process for the next vertex.

**Syntax**:

.. code::

    random(<stop_conditions>)

**Examples**:

Walk randomly until the path sequence has reached a length of 100 elements.

.. code::

    random(length(100))

Walk randomly and never stop.

.. code::

    random(never)


Weighted Random
~~~~~~~~~~~~~~~

Same as the random path generator, but will use weights when generating a
path. A weight is assigned to an edge, and it represents the probability
of an edge getting chosen.

**Syntax**:

.. code::

    weight_random(<stop_conditions>)

**Examples**:

Walk randomly with weights until the path sequence has reached a length of 100
elements.

.. code::

    weight_random(length(100))

Walk randomly with weights and never stop.

.. code::

    weight_random(never)

Quick Random
~~~~~~~~~~~~

Tries to run the shortest path through a model. This is how
the algorithm works:

1. Choose randomly an edge not yet visited.
2. Select the shortest path to that edge using `Dijkstra's algorithm <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>`_.
3. Walk that path, and mark all the executed edges as visited.
4. When reaching the selected edge in step 1, start all over.

The algorithm works well for very large models, and generates reasonably short
sequences.

The downside is when used in conjunction with **guards**, the
algorithm can choose a path which is blocked by a guard.

**Syntax**:

.. code::

    quick_random(<stop_conditions>)

**Examples**:

Randomly chooses an edge not visited until the path sequence has reached a
length of 100 elements.

.. code::

    quick_random(length(100))

Randomly chooses an edge not visited until the vertex coverage has reached 100%.

.. code::

    quick_random(vertex_coverage(100))

A Star
~~~~~~

Generates the shortest path to a specific vertex or edge, using the
`A* search algorithm <https://en.wikipedia.org/wiki/A*_search_algorithm>`_.

**Syntax**:

.. code::

    a_star(<stop_conditions>)

.. note::

    The *A start* generator must use a stop condition that names a vertex
    or an edge (``reached_vertex`` or ``reached_edge``).


**Examples**:

Walks the shortest path to the vertex ``v_name`` and then stops.

.. code::

    a_star(reached_vertex(v_name))

Walks the shortest path to the edge ``e_name`` and then stops.

.. code::

    a_star(reached_edge(e_name))



Stop Conditions
---------------

A **stop condition** is responsible for deciding when a path is completed. The
**generator** will generate a new step in the path until the **stop condition**
is fulfilled.

Vertex Coverage and Edge Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vertex coverage and edge coverage stop conditions take as arguments a
percentage. The path is completed when the percentage of traversed
elements is reached.

If an element is traversed more than once, it still counts as 1 when
calculating the percentage coverage.

**Syntax**:

.. code::

    vertex_coverage(<percentage>)

.. code::

    edge_coverage(<percentage>)

**Examples**:

Randomly chooses an edge not visited until the vertex coverage has reached 50%.

.. code::

    quick_random(vertex_coverage(50))


Walks randomly until the edge coverage has reached 75%.

.. code::

    random(edge_coverage(75))


Requirement Coverage
~~~~~~~~~~~~~~~~~~~~

This stop condition takes as an argument a percentage.

The path is completed when the percentage of traversed requirements is reached.
If a requirement is traversed more than once, it still counts as 1 when
calculating the percentage covered.

**Syntax**:

.. code::

    requirement_coverage(<percentage>)

**Examples**:

Walks randomly until the requirements coverage has reached 25%.

.. code::

    random(requirement_coverage(25))


Dependency Edge Coverage
~~~~~~~~~~~~~~~~~~~~~~~~

This stop conditions takes an integer as argument representing the
dependency threshold.

The path is completed when all of the traversed edges with dependency higher or
equal to the threshold are reached.

**Syntax**:

.. code::

    dependency_edge_coverage(<dependency_threshold>)

**Examples**:

Walks randomly until all the edges with dependency higher or equal to 85%
are reached.

.. code::

    random(dependency_edge_coverage(85))


Reached Vertex and Reached Edge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reached vertex and reached edge stop conditions take as argument a name of
an element.

The path is completed when the element is reached.

**Examples**:

Walks randomly until the vertex ``v_name`` is reached.

.. code::

    random(reached_vertex(v_name))

Walks the shortest path to the edge ``e_name`` and then stops.

.. code::

    a_star(reached_edge(e_name))


Time Duration
~~~~~~~~~~~~~

Time duration stop condition takes as argument a number of seconds, representing
the time that the test generator is allowed to execute.

Please note that the time is compared with the execution for the whole test.
This means that if you for example have:

* 2 models with common shared states
* both having ``time_duration`` stop condition set to 60 seconds

Then both models will stop executing after 60 seconds, even if one of the
models have not been visited.

.. warning::

    The ``time_duration`` stop condition is not allowed with ``offline`` mode.


**Examples**:

Walks randomly for 500 seconds:

.. code::

    random(time_duration(500))


Length
~~~~~~

Length stop condition takes an integer as argument, representing the total
numbers of edge-vertex pairs generated by a generator.

For example, if the number is 110, the test sequence would be 220 elements
(110 pairs of edges and vertices).

**Examples**:

Walks randomly until the path sequence has reached a length of 24 elements:

.. code::

    random(length(24))

Never
~~~~~

This special stop condition will never stop the generator.


.. warning::

    The ``never`` stop condition is not allowed with ``offline`` mode.


**Examples**:

Walks randomly forever:

.. code::

    random(never)


Combining Stop Conditions
-------------------------

Multiple stop conditions can be set using logical `or`, `and`, `||`, `&&`.

**Examples**:

Walks randomly until the edge coverage has reached 100%, or we have
executed for 500 seconds.

.. code::

    random(edge_coverage(100) or time_duration(500))

Walks randomly until the edge coverage has reached 100%, and it reached
the vertex: ``v_name``.

.. code::

    random(reached_vertex(v_name) && edge_coverage(100))

Chaining Generators
-------------------

Generators can be chained one after another.

**Examples**:

Walks randomly until the edge coverage has reached 100% and
it reached the vertex: ``v_name``. Then starts walking randomly
for 1 hour.

.. code::

    random(reached_vertex(v_name) and edge_coverage(100)) random(time_duration(3600))


Further Reading/Useful Links
----------------------------

* `GraphWalker Documentation on Generators and Stop Conditions <https://github.com/GraphWalker/graphwalker-project/wiki/Generators-and-stop-conditions>`_
* `A* search algorithm <https://en.wikipedia.org/wiki/A*_search_algorithm>`_
* `Dijkstra's algorithm <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>`_
