==========================
Frequently Asked Questions
==========================

`Contact us <altwalker@altom.com>`_ or go to our `Gitter chat room <https://gitter.im/altwalker/community>`_ if you have any question ideas.

How to reuse the same method for two (or more) elements?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you add two (or more) elements with the same ``name`` (but diffrent ``id``)
in your model, both elements will be mapped to the same method.

You can use this technique for actions that can happen on different
states of the application. For example an ``e_go_back`` edge that
will press the back button from multiple pages.
