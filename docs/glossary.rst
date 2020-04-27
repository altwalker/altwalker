:orphan:

Glossary
========

.. glossary::

    SUT
    AUT
        *Application/System Under Test* refers to a application/system being tested.

    FSM
        A *Finite State Machines* it is an abstract machine that can be in exactly
        one of a finite number of states at any given time. The FSM can change from
        one state to another in response to some inputs; the change from one state to
        another is called a transition.

    Directed Graph

        A *Directed Graph* is a graph that is made up of a set of vertices connected
        by edges, where the edges have a direction associated with them.

    MBT
        *Model-Based Testing* is a testing technique which offers a way of generating
        test cases based on models that describe the behaviour (functionality) of the
        system under test.

    Model
        The *Model* is an abstract representation of the behaviors and functionalities
        of the :term:`SUT`. AltWalker uses :term:`FSM` for the models.

    Modeling
        *Modeling* is the process of translating the behaviors and functionalities of the
        :term:`SUT` into an abstract model.

    Test Fixture
        A *Test Fixture* represents the preparation needed to perform one or more tests,
        and any associate cleanup actions.

    Test Case
        A *Test Case* is the individual unit of testing. It checks for a specific response
        to a particular set of inputs.

    Test Runner
        A *Test Runner* is a component which orchestrates the execution of tests and provides
        the outcome to the user.
