# Use actions and guards

__Actions__ and __Guards__ provide a way to split the test based on the data which you use. That
approach allows you to reuse/combine/change the data for each test separately. It lets you
to test login with different credentials, or iteration through boundary values and
equivalent classes.

```eval_rst
.. contents:: Table of Contents
    :local:
    :backlinks: none
```

## Overview

GraphWalker keeps a context for each model plus a global context. A context is a set of variables.

GraphWalker has two way to interact with the data from the context:

1. __Actions__ allow you to initialize and update the data from the context.
1. __Guard__ allows you to block (guard) edges until a condition is meet.

Each model has a unique set of variables, so if you want to use variables across models
you must save them in the global context. Every variable of the form `global.<variable-name>` is
saved in the global context (e.g. ``global.count``, ``global.isLoggedIn``).

```eval_rst
.. note::
    Throughout the documentation the data from the context is usually referred as `graph data`
    or just `data`.
```

### Actions

An __action__ is a pice of Java code executed by GraphWalker. You can place
action on the model level which well be executed before any step from that model or
on an edge which will be executed when an edge is reached.

__Examples__:

```json
{
    "actions": [
        "global.count++;",
        "isUserLoggedIn = false;"
    ]
}
```

```eval_rst
.. note::
  Each action must end with ``;`` (e.g. ``count++;`` is a valid action while ``count++`` is not).
```

### Guards

A __guard__ is a pice of Java code which if evaluates as `false` marks an _edge_ as unreachable,
the __guard__ can use the variables from the context of the current model of the global context.

__Examples__:

```json
{
    "guard": "isUserLoggedIn == false",
}
```

```json
{
    "guard": "globbal.count > 10",
}
```

## Log In Example

Let’s consider the model below which has a login test (`v_logged_in`) and a logout test (`v_logged_out`).
Note that the two vertices could reference another models with the rest of the functionality, for
logged in users respectively logged out users, but for the simplicity of the example we are using only two
vertices.

```json
{
    "name": "Action and Guards Example",
    "models": [
        {
            "name": "LoginModel",
            "generator": "random(never)",
            "startElementId": "v_0",
            "actions": [
            	"isUserLoggedIn = false;"
            ],
            "vertices": [
                {
                    "id": "v_0",
                    "name": "v_start"
                },
                {
                    "id": "v_1",
                    "name": "v_app"
                },
                {
                    "id": "v_2",
                    "name": "v_logged_in"
                },
                {
                    "id": "v_3",
                    "name": "v_logged_out"
                }
            ],
            "edges": [
                {
                    "id": "e_0",
                    "name": "e_open_app",
                    "sourceVertexId": "v_0",
                    "targetVertexId": "v_1"
                },
                {
                    "id": "e_1",
                    "name": "e_log_in",
                    "guard": "isUserLoggedIn == false",
                    "actions": [
                        "isUserLoggedIn = true;"
                    ],
                    "sourceVertexId": "v_1",
                    "targetVertexId": "v_1"
                },
                {
                    "id": "e_2",
                    "name": "e_log_out",
                    "guard": "isUserLoggedIn == true",
                    "actions": [
                        "isUserLoggedIn = false;"
                    ],
                    "sourceVertexId": "v_1",
                    "targetVertexId": "v_1"
                },
                {
                    "id": "e_3",
                    "name": "e_for_user_logged_in",
                    "guard": "isUserLoggedIn == true",
                    "sourceVertexId": "v_1",
                    "targetVertexId": "v_2"
                },
                {
                    "id": "e_4",
                    "name": "e_for_user_not_logged_in",
                    "guard": "isUserLoggedIn == false",
                    "sourceVertexId": "v_1",
                    "targetVertexId": "v_3"
                }
            ]
        }
    ]
}
```

The idea is that:

* At first `isUserLoggedIn` is set to `false`.
* Go on `v_start` which is the starting point.
* Go on `e_open_app` and launch the application.
* Now we are on the `v_app` vertex.

And from here there are two paths:

* Now we can go on `e_for_user_not_logged_in` edge for which the guard condition (`isUserLoggedIn == false`) is meet.
* Now we are on `v_logded_out` where we have some test which don't need a logged in user.

Or:

* Go on the `e_log_in` edge, wich will set `isUserLoggedIn` to `true`.
* Now we can go on `e_for_user_logged_in` edge because the guard condition (`isUserLoggedIn == true`) is meet.
* Now we are on `v_logded_in` where we have some test for a logged in user.

## Further Reading/Useful Links

* GraphWalker documentation on:
    * [Tests parametrisation](http://graphwalker.github.io/tests_parametrisSation/)
    * [JSON File Format](http://graphwalker.github.io/json-overview/)
* AltWalker documentation on:
    * [Modeling](../../modeling.md)
