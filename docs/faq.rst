==========================
Frequently Asked Questions
==========================

`Contact us <altwalker@altom.com>`_ or go to our `Gitter chat room <https://gitter.im/altwalker/community>`_ if you have any question ideas.

What is the diference betwen AltWalker and GraphWalker?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**GraphWalker** is an Model-Based Testing tool. It reads models in the shape
of directed graphs, generates (tests) paths from these graphs and supports running
tests in written in Java.

**AltWalker** is a :term:`test runner` it uses GraphWalker for path generation and
adds support for generating and runnig tests written in python3 and C#/.NET with
the option of adding support for other languages (by writing your own executor).

How to reuse the same method for two (or more) elements?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you add two (or more) elements with the same ``name`` (but diffrent ``id``)
in your model, both elements will be mapped to the same method.

You can use this technique for actions that can happen on different
states of the application. For example an ``e_go_back`` edge that
will press the back button from multiple pages.
