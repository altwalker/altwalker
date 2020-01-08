Pass environment variables to your tests
-------------

Running your tests may require different test context based on your environment. You may want to have different configurations options which you pass as variables, or you write them in a configuration file. You can pass environment variables to your tests using AltWalker.

Setting environment variable

.. tabs::
    .. group-tab:: MacOS/Linux

        .. code-block:: console

            $ export TESTS_CONF_FILE="conf.production.json"
            $ altwalker online tests -m models.json "random(vertex_coverage(30))"


    .. group-tab:: Windows

        .. code-block:: console

            > set TESTS_CONF_FILE="conf.production.json"
            > altwalker online tests -m models.json "random(vertex_coverage(30))"


Accessing environment variable in your tests

.. tabs::
    .. group-tab:: Python

        .. code-block:: py

            conf_file = os.environ.get("TESTS_CONF_FILE", "conf.development.json")
        

    .. group-tab:: C#

        .. code-block:: c#

            var confFile = Environment.GetEnvironmentVariable("TESTS_CONF_FILE") ?? "conf.development.json";