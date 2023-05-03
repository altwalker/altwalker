==========================
Frequently Asked Questions
==========================

Welcome to the AltWalker FAQ! Here are some answers to common questions about using AltWalker.

`Contact us <altwalker@altom.com>`_ or go to our `Gitter chat room <https://gitter.im/altwalker/community>`_ if you have any questions.


What is Model-Based Testing?
============================

Model-Based Testing is an approach to software testing that uses models (such
as directed graphs) to generate test cases. This method is useful because it
can help ensure that all possible paths through the software are tested, leading
to more comprehensive test coverage and higher-quality software.


What's the difference between AltWalker and GraphWalker?
========================================================

**TL;DR**: AltWalker is a wrapper for GraphWalker that adds support for running tests
written in Python3 and C#/.NET.

**GraphWalker** is an Model-Based Testing tool. It reads models in the shape
of directed graphs, generates (tests) paths from these graphs and supports running
tests in written in Java.

**AltWalker** is a :term:`test runner` it uses GraphWalker for path generation and
adds support for generating and running tests written in Python3 and C#/.NET with
the option of adding support for other languages (by writing your own executor).


What are some of the key features of AltWalker?
===============================================

AltWalker offers several useful features for software testing, including:

* Support for generating and running tests written in Python3 and C#/.NET.
* The option of adding support for other languages by writing your own executor.
* A powerful, easy-to-use CLI (command-line interface) for running tests.
* Seamless integration with other testing tools, such as `Selenium`_ and `Appium`_.


Can I use Appium/Selenium with AltWalker?
=========================================

Yes, AltWalker does not interact with your :term:`SUT` (System Under Test). You need some
other tool to do that. If, for instance, you want to test a web application, you would
perhaps use `Selenium`_ to do that, or if your target is a mobile app, then `Appium`_ might be
your choice.


How to reuse the same method for two (or more) elements?
========================================================

If you add two (or more) elements with the same ``name`` (but different ``id``)
in your model, both elements will be mapped to the same method.

You can use this technique for actions that can happen on different
states of the application. For example an ``e_go_back`` edge that
will press the back button from multiple pages.


How do I get help or support for AltWalker?
===========================================

If you have any questions or need help with AltWalker, you can contact us at
`altwalker@altom.com <altwalker@altom.com>`_ or join our `Gitter chat room <https://gitter.im/altwalker/community>`_.
Our team is happy to assist you with any issues you may encounter.


.. _Appium: https://appium.io/
.. _Selenium: https://www.selenium.dev/
