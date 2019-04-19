# Quickstart

In this quickstart you will learn how to create your tests project from scratch, from an
existing model or to generate a code template for your models and run your tests with AltWalker.

```eval_rst
.. contents:: Table of Contents
    :local:
    :backlinks: none
```

## Python

### Start from scratch

```
$ altwalker init test-project
```

The `init` command creates tests directory and initialize a git repository. The tests directory contains a sample model (`test-project/models/default.json`) and a python package package containing the template code for the model (`test-poject/tests`).

To run the tests for the `default.json` model, run the following commands:

```
$ cd test-project
$ altwalker online tests -m models/default.json "random(edge_coverage(100))"
```

The online command runs your tests inside `tests` with the `default.json` model using the `random(edge_coverage(100))` stop condtion.

### Start from an existing model

```
$ altwalker init test-project -m path/to/model.json
```

The `init` command creates a tests directory with your model(s), generates the code template for the model(s) and initialize a git repository.

After you create a tests directory, you can run your tests:

```
$ cd test-project
$ altwalker online tests -m models/model.json "random(vertex_coverage(100))"
```

### Generate a code template for your models

```
$ altwalker generate path/for/package/ -m path/to/models.json
```

The `generate` command will generate a test package named `tests` containing the code template for the modele(s), inside the `path/for/package/` directory.

## C#/.NET

### Start from scratch

```
$ altwalker init -l c# test-project
```

The `init` command creates `test-project` directory and initialize a git repository. The directory contains a C# project refering `altwalker.executor` from nuget, a class for each model,`Program.cs`, and a simple model file `models/default.json` to get you started.

```
/test-project/test-project/test-project.csproj
/test-project/test-project/ModelName.cs
/test-project/test-project/Program.cs
/test-project/models/default.json
```

The `Program.cs` containing the entry point of the tests and starts the `ExecutorService`.

```c#
public class Program {
    public static void Main (string[] args) {
        ExecutorService service = new ExecutorService();
        service.RegisterModel<DefaultModel>();
        service.Start(args);
    }
}
```

To run the tests for the `default.json` model, run the following commands:

```
$ cd test-project
$ altwalker online -x dotnet test-project -m models/default.json "random(edge_coverage(100))"
```

The `online` command runs the tests using AltWalker's .NET executor with the `default.json` model using the `random(edge_coverage(100))` stop condition.

### Start from an existing model

```
$ altwalker init -l c# test-project -m path/to/model.json
```

The `init` command creates `test-project` directory and initialize a git repository. The directory contains a C# project referring `altwalker.executor` from NuGet, a class for each model, and `Program.cs`.

The `Program.cs` containing the entry point of the tests and starts the `ExecutorService`.

```c#
public class Program {
    public static void Main (string[] args) {
        ExecutorService service = new ExecutorService();
        service.RegisterModel<DefaultModel>();
        service.Start(args);
    }
}
```

After you create a tests directory, you can run your tests:

```
$ cd test-project
$ altwalker online -x dotnet test-project -m models/model.json "random(vertex_coverage(100))"
```

### Generate a code template for your models

```
$ altwalker generate -l c# path/for/test-project/ -m path/to/models.json
```

The `generate` command creates `path/for/test-project` directory containing `test-project.csproj` file, `Program.cs` and the code template for the model(s).

## Next Steps

Depending on how new you are to AltWalker you can read about how to design your models on the [Modeling](./modeling) section, how to structure your tests on the
[Test Structure](./tests-structure) section, checkout the [Examples](./examples), or dig deeper into the [Command Line Interface](./cli).
