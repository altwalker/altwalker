# Write your own executor

The AltWalker executor is responsible for executing your tests. AltWalker provides you with
a Python and .NET executor by default. You can hook up your own executor via HTTP.

Your HTTP executor should be able to create a test execution context and execute tests.
The context is initialized with path to tests provided via load route.

```eval_rst
.. contents:: Table of Contents
    :local:
    :backlinks: none
```

## Executor Routes

__Root URL__: `/altwalker`

### Load

Should load test code from a given path. AltWalker calls load with the `TEST_PACKAGE` argument given to the `verify`, `online` and `walk` commands.

* __URL__: `/load`
* __Method__: `POST`
* __Data Params__:

    ```json
    {
        "path": "..."
    }
    ```

* __Success Response__:
    * __Code__: 200

* __Error Response__:
    * __Codes__:
        * `463`: Path Not Found
        * `464`: Load Error (in case the path to load is invalid)

* __Sample Call__:

    ```
    $ curl -X POST -d '{"path": "path/to/my/tests"}}' -H 'Content-Type: application/json'  http://localhost:4200/altwalker/load
    ```

### Reset

Should resets the current execution context.

* __URL__: `/reset`
* __Method__: `PUT`
* __Success Response__:
    * __Code__: 200

* __Error Response__:
    * __Codes__:
        * `465`: No Test Code Loaded

* __Sample Call__:

    ```
    $ curl -X PUT http://localhost:4200/altwalker/reset
    ```

### Has Model

Should checks if a model exists.

Is used by the `verify` command.

* __URL__: `/hasModel`
* __Method__: `GET`
* __URL Params__:

    Required:

    `name=[string]`

* __Success Response__:
    * __Code__: 200
    * __Content__:

    ```json
    {
        "payload": {
            "hasModel": true
        }
    }
    ```

* __Sample Call__:

    ```
    $ curl http://localhost:4200/altwalker/hasModel?name="ModelName"
    ```

### Has Step

Should checks if a step exists. Is used by the `verify` command.

* __URL__: `/hasStep`
* __Method__: `GET`
* __URL Params__:

    Required:

    `name=[string]`

    Optional:

    `modelName=[string]`

    The `modelName` is not needed for `setUpRun` and `tearDownRun`.

* __Success Response__:
    * __Code__: 200
    * __Content__:

    ```json
    {
        "payload": {
            "hasStep": true
        }
    }
    ```

* __Sample Call__:

    ```
    $ curl http://localhost:4200/altwalker/hasStep?name="setUpRun"
    ```

    ```
    $ curl http://localhost:4200/altwalker/hasStep?name="setUpModel"&modelName="ModelName"
    ```

### Execute Step

Should executes the step. Is used by the `online` and `walk` commands.

* __URL__: `/executeStep`
* __Method__: `POST`
* __URL Params__:

    Required:

    `name=[string]`

    Optional:

    `modelName=[string]`

    The `modelName` is not needed for `setUpRun` and `tearDownRun`.

* __Data Params__:

    ```json
    {
        "data": {
            "key": "value"
        }
    }
    ```

    The data is a key value dictionary containing the data form the current model.

* __Success Response__:
    * __Code__: 200
    * __Content__:

    ```json
    {
         "paylod": {
            "output": "",
            "data": {
            },
            "result": {
            },
            "error": {
                "message": "",
                "trace": ""
            }
         }
    }
    ```

    The `output` is the output of the step. It is required.

    The `data` key from the response should be the data modified by your tests. It is not required.

    The `result` is the value returned by the step. It is not required. It can be of any type.

    The `error` key should be present only if the step failed.

* __Error Response__:
    * __Codes__:
        * `460`: Model Not Found
        * `461`: Step Not Found
        * `462`: Invalid Step Handler (in case a method with the name of Step exists but requires invalid arguments)


* __Sample Call__:

    ```
    $ curl -X POST -d '{"data": {"key": "value"}}' -H 'Content-Type: application/json'  http://localhost:4200/altwalker/hasStep?name="setUpModel"&modelName="ModelName"
    ```

## Error Status Codes

In case of any error in the Http executor, a status code and a json body is expected by AltWalker.

* `404`: Not Found (for unhandled urls)
* `460`: Model Not Found
* `461`: Step Not Found
* `462`: Invalid Step Handler (in case a method with the name of Step exists but requires invalid arguments)
* `463`: Path Not Found
* `464`: Load Error (in case the path to load is invalid)
* `465`: No Test Code Loaded
* `500`: Unhandled Exception

__Response Body__:

```json
{
    "error": {
        "message": "...",
        "trace": "..."
    }
}
```

## Using your executor

```
$ altwalker online -x http --url http://localhost:4200/ -m path/to/model.json "generator(stop_condition())" path/to/my/tests
```

* `-x http`

    Use the http executor.

* `--url http://localhost:4200/`

    The url where your executor is listening.

* `path/to/my/tests`

    The path to your tests, relative to your executor location. This is passed to your executor via POST `/load`.

## Further Reading/Useful Links

Check [altwalker.executor.HttpExecutor](../api.html#altwalker.executor.HttpExecutor) to see the HttpExecutor client.
