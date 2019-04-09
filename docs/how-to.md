# How To's

## Write your own executor 

The AltWalker executor is the module responsible for executing your tests. Altwalker provides you with a python and dotnet executor by default. You can hook up your own executor via HTTP.

Your HTTP executor should be able to create a test execution context and execute tests. 
The context is initialized with path to tests provided via load route.



### Executor Routes

* POST `/load`

Recieves the path to the tests. Loads the execution context with tests from the provided `path`.

    Post body: 

    ```json
    {
        "path": "..."
    }
    ```

* PUT `/reset`

Resets the current execution context.

* GET `/hasModel?name=<name>`

Checks if the model exists

    Response body:

    ```json
    {
        "payload": {
            "hasModel": true/false
        }
    }
    ```

* GET `/hasStep?modelName=<modelName>&name=<name>`

Checks if step exists 

    Response body:
    
    ```json
    {
        "payload": {
            "hasStep": true/false
        }
    }
    ```

* POST `/executeStep?modelName=<modelName>&name=<name>`

Executes the step. The data is a key value dictionary that carries data modified by your tests, or by actions in your models.

    Post body: 

    ```json
    {
        "data": {
            ...
        } 
    }
    ```

    Response body:

    ```json
    {
         "paylod": {
             "data": {
                 ...
             },
             "output": "",
             "error": {
                 "message": "",
                 "trace": "" 
             }
         }
    }
    ```

Check [altwalker.executor.HttpExecutor](api.html#altwalker.executor.HttpExecutor) to see the HttpExecutor client.

### HTTP Error status codes

In case of any error in the Http executor, a statuscode and a json body is expected by AltWalker.

* `404` Not Found (unhandled urls)
* `460` Model Not Found 
* `461` Step Not Found
* `462` Invalid StepHandler - in case a method with the name of Step exists but requires invalid arguments
* `463` Path Not Found
* `464` Load Error - in case the path to load is invalid
* `465` No Test Code Loaded
* `500` Unhandled Exception


Response body:
```json
{
    "error": {
        "message": "",
        "trace": "" 
    }
}
```

### Using your executor

`altwalker online -x http --base-url http://localhost:4200/ -m path/to/model.json "generator(stop_condition())" path/to/my/tests`

    -x http                              Use the http executor
    --base-url http://localhost:4200/    The url where your executor is listening
    -m path/to/model.json                The path to your model
    path/to/my/tests                     The path to your tests, relative to your executor location. This is passed to your executor via POST /load