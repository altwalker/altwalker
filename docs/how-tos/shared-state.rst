=================
Use shared states
=================

**Shared states** provide a way to split your models into smaller models that are linked together
by one vertex from each model that have the same **shared state**.

.. contents:: Table of Contents
    :local:
    :backlinks: none

Overview
--------

GraphWalker allows you to link together two (or more) models with a **shared state**. Each *shared state* has a name
that identifies it, all vertices that have the same name are linked together.

If two (or more) vertices have the same **shared state** now the path can jump from one vertex to another.

.. note::

    When you are using a *shared state* between two or more vertices the path can jump from one to every other one.

**Examples**:

.. code-block:: json

    {
        "id": "v_0",
        "name": "v_link_a",
        "sharedState": "link"
    }


.. code-block:: json

    {
        "id": "v_1",
        "name": "v_link_b",
        "sharedState": "link"
    }

Now when generating a path you can have a jump from ``v_0`` to ``v_1`` or from ``v_1`` to ``v_0``.


Blog example
------------

Let’s consider the models below the ``Navigation`` model where we model the navigation for our blogging
website (for simplicity we make only one vertex and edge) and the ``PostBlog`` model where we model
the posting of a new blog.

Model visualization:

.. figure:: ../_static/img/blog-model.png

    Screenshot taken from the Model-Editor.

Model source:

.. literalinclude:: ../_static/models/blog.json
    :language: json
    :emphasize-lines: 12, 41


Now we separated the navigation of the home page from the blogging, this way our models are easier to
implement and maintain.

You can also split the models in two different files one for each model:

In ``blog-navigation.json`` will save the ``Navigation`` model:

.. literalinclude:: ../_static/models/blog-navigation.json
    :language: json


And in ``blog-post.json`` will save the ``PostBlog`` model:

.. literalinclude:: ../_static/models/blog-post.json
    :language: json

Splitting the models in two files allows us the flexibility to choose to generate a path form only one model
or form both.

**Examples**:

.. code-block:: console

    $ altwalker offline -m blog-navigation.json "random(length(24))"

.. code-block:: console

    $ altwalker offline -m blog-navigation.json "random(length(24))" \
                        -m blog-post.json "random(length(24))"


.. note::

    We consider a good practice to split each model into its own file.


.. only:: builder_html

    .. admonition:: And, by the way...

        You can download the models:

            * :download:`blog.json <../_static/models/blog.json>`
            * :download:`blog-navigation.json <../_static/models/blog-navigation.json>`
            * :download:`blog-post.json <../_static/models/blog-post.json>`

        And use the ``init`` command to generate a project from the model (for python or c#):

        .. tabs::

            .. group-tab:: Python

                .. code-block:: console

                    $ altwalker init shared-states-example -m blog.json -l python

                Or:

                .. code-block:: console

                    $ altwalker init shared-states-example -l python \
                        -m blog-navigation.json \
                        -m blog-post.json

            .. group-tab:: C#/.NET

                .. code-block:: console

                    $ altwalker init shared-states-example -m blog.json -l c#

                Or:

                .. code-block:: console

                    $ altwalker init shared-states-example -l c# \
                        -m blog-navigation.json \
                        -m blog-post.json

        And then you can run the example.

        If you need help with the ``init`` command check out the :doc:`../quickstart` section.


Further Reading/Useful Links
----------------------------

* GraphWalker Documentation for `JSON vertex format <https://github.com/GraphWalker/graphwalker-project/wiki/JSON-file-format%3A-vertex>`_.
* AltWalker Documentation for :doc:`../core/modeling`.
