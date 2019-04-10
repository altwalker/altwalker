# Contributing

First off, thank you for considering contributing to AltWalker.

## Did you find a bug?

* Ensure the bug was not already reported by searching all [issues](https://gitlab.com/altom/altwalker/altwalker/issues).
* If you're unable to find an open issue addressing the problem, open a new one and label it with the bug label. Be sure to include a title and clear description, as much relevant information as possible:
    * What version of python are you using?
    * What operating system are you using?
    * What did you do?
    * What did you expect?
    * A code sample or an executable test case demonstrating the expected behavior that is not occurring.

When you ask a question about a problem you will get a much better/quicker answer if you provide a code sample that can be used to reproduce the proble. Try to:

* Use as little code as possible that still produces the same problem.
* Provide all parts needed to reproduce the problem (code and model if needed).
* Test the code you’re about to provide to make sure it reproduces the problem.

## How to suggest a feature or enhancement?

If you find yourself wishing for a feature that doesn't exist in AltWalker:

* Ensure the enhancement was not already reported by searching all [issues](https://gitlab.com/altom/altwalker/altwalker/issues).
* Open an issue on our [issues list](https://gitlab.com/altom/altwalker/altwalker/issues) and label it with the enhancement lable. Be sure to include a clear description of the feature you would like to see, as much relevant information as possible:
    * Why you need it?
    * How it should work?

## You need your custom test executor?

You can implement your own custom test execution by implementing a server for the executor's http protocol.

In order to run tests (for other languages except Python) AltWalker communicates with an http executor. To implement a test executor you need to create a http server that implements the protocol used by AltWalker.

Check [altwalker.executor.HttpExecutor](https://altom.gitlab.io/altwalker/altwalker/api.html#altwalker.executor.HttpExecutor) for communication protocol.

## Submit a test executor in another language?

If you've implemented your own custom test executor in a language that is not already supported by AltWalker [contact us](mailto:altwalker@altom.com) and will help you integrate it.