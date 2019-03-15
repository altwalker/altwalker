# Tests Structure


## Structure

AltWalker requires a python package (usually name ``tests``) and inside a
python module named ``test.py``:

```
project-root/
    tests/
        __init__.py
        test.py
```

Inside `test.py` each model is implemented in a class, and each
vertex/edge in a method inside the class.

```python
# tests/test.py

class ModelA:
    """The implementation of the model named ModelA."""

    def vertex_a(self):
        """The implementation of the vertex named vertex_a form ModelA."""

    def edge_a(self):
        """The implementation of the edge named edge_a form ModelA."""


class ModelB:
    """The implementation of the model named ModelB."""

    def vertex_b(self):
        """The implementation of the vertex named vertex_b form ModelB."""

    def edge_b(self):
        """The implementation of the edge named edge_b form ModelB."""
```


## Fixtures

AltWalker implements four test fixtures inspired by JUnit and the python unittest
module:

* `setUpRun`
* `tearDownRun`
* `setUpModel`
* `tearDownModel`

All test fixtures are optional.

```python
# tests/test.py

def setUpRun():
    """Will be executed first, before anything else."""

def tearDownRun():
    """Will be executed last."""


class ModelA:

    def setUpModel(self):
        """Will be executed before executing any step from this model."""

    def tearDownModel(self):
        """Will be executed after executing all steps from this model."""

    def vertex_a(self):
        pass

    def edge_a(self):
        pass
```

## Graph Data

If you are using the `online` command your test code has direct access to the  graphs
execution context provided by GraphWalker.

In order to read/update the graph data from you tests, you need to define the function with
a parameter, and AltWalker will pass a [`GraphData`](./api.html#module-altwalker.data) object,
that object allows you to read and update the graph data.

```python
def element_method(self, data):
    """A simple example of a method for a vertex/edge inside a model.

    Args:
        data: AltWalker will pass an GraphData object.
    """

    # to get all available data
    graph_data = data.get()

    # to get the value for a single key
    value = data.get("key")

    # to set a new value for a key
    data.set("key", "new_value")
```
