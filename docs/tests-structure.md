# Tests Structure

```eval_rst
.. contents:: Table of Contents
    :local:
    :backlinks: none
```

## Python

### Structure

AltWalker requires a python package (usually named `tests`) and inside a
python module named `test.py`:

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

### Fixtures

AltWalker implements four test fixtures inspired by JUnit and the python unittest
module:

- `setUpRun`
- `tearDownRun`
- `setUpModel`
- `tearDownModel`

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

### Graph Data

If you are using the `online` command your test code has direct access to the graphs
execution context provided by GraphWalker.

In order to read/update the graph data from you tests, you need to define the function with
a parameter, and AltWalker will pass a `dict` object,
that object allows you to read and update the graph data.

```python
def element_method(self, data):
    """A simple example of a method for a vertex/edge inside a model.

    Args:
        data: AltWalker will pass a dict object.
    """

    # to get the value for a single key
    value = data["key"]

    # to set a new value for a key
<<<<<<< HEAD
    data["strVariable"] = "new_value"
    data["intVariable"] = 1
    data["boolVariable"] = True
```

```eval_rst
.. warning::

    Note that you can set key to ``str``, ``int`` or ``bool``, but GraphWalker will always return ``str``.

    So you have to convert your values back to ``int`` or ``bool``.

    * for ``int``:

    .. code-block:: python

        value = int(data["integer"])

    * for ``bool``:

    .. code-block:: python

        value = data["boolean"] == "true"
=======
    data["key"] = "new_value"
>>>>>>> master
```

## C#/.NET

### Structure

To run C# tests, AltWalker requires a c# console application that depends on [`altwalker.executor`](https://gitlab.com/altom/altwalker/dotnet-executor) NuGet and runs the `ExecutorService`.

```c#
/// The implementation of the model named ModelA.
public class ModelA{
    /// The implementation of the vertex named vertex_a.
    public void vertex_a() {}

    /// The implementation of the edge named edge_a
    public void edge_a() {}
}

public class Program {
        public static void Main (string[] args) {
            ExecutorService service = new ExecutorService();
            service.RegisterSetup<Setup>();
            service.Start(args);
        }
    }
```

`altwalker.executor` targets .netstandard 2.0

### Fixtures

Define `setUpModel` and `tearDownModel` inside the model class. This methods will run before and after all steps from model have run.

Define `setUpRun` and `tearDownRun` inside a Setup class, and register it inside the executor service: `ExecutorService.RegisterSetup<T>();`

```c#
/// The implementation of the model named ModelA.
public class ModelA {
    /// Will be executed before executing all steps from this model
    public void setUpModel() {}

    /// Will be executed after executing all steps from this model
    public void tearDownModel() {}
}

public class Startup {
    /// Will be executed first, before anything else.
    public void setUpRun() {}

    /// Will be executed first, after anything else.
    public void tearDownRun() {}
}

public class Program {
        public static void Main (string[] args) {
            ExecutorService service = new ExecutorService();
            service.RegisterModel<MyModel>();
            service.RegisterSetup<Setup>();
            service.Start(args);
        }
    }
```

### Graph Data

If you are using the `online` command your test code has direct access to the graphs
execution context provided by GraphWalker.

In order to read/update the graph data from you tests, you need to define the function with
a parameter, and AltWalker will pass a `IDictionary<string, dynamic>` object,
that object allows you to read and update the graph data.

```c#
public void vertex_a(IDictionary<string, dynamic> data)
{
    data["passed_vertex_a"]=true;
}
```
