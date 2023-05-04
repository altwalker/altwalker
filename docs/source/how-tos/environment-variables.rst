================================================
How to: Pass environment variables to your tests
================================================

Running your tests may require different test context based on your
environment. You may want to have different configurations options which
you pass as environment variables, or you write them in a configuration file.

Setting environment variable:

.. tab:: MacOS/Linux

    .. code-block:: console

        $ export TESTS_CONF_FILE="conf.production.json"
        $ altwalker online tests -m models/models.json "random(vertex_coverage(30))"

.. tab:: Windows

    .. code-block:: console

        > set TESTS_CONF_FILE="conf.production.json"
        > altwalker online tests -m models/models.json "random(vertex_coverage(30))"


Accessing environment variable in your tests:

.. tab:: Python

    .. code-block:: py

        config_file = os.environ.get("TESTS_CONF_FILE", "conf.development.json")

.. tab:: C#

    .. code-block:: c#

        var configFile = Environment.GetEnvironmentVariable("TESTS_CONF_FILE") ?? "conf.development.json";
