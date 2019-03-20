# Demo

## Ecommerce Demo

[Source Code](https://gitlab.com/altom/altwalker/altwalker-examples/tree/master/ecommerce-snipcart-jekyll-example)

In this example you will learn how to model your ecommerce website tests as a directional graph, how to use Actions, Guards and Shared State in your graph model. You will learn how to use AltWalker's `online`, `offline`, `walk`, `check` and `verify` commands.

The tests are written in python with selenium and python page object model (pypom). The ecommerce website beeing tested is written in markdown and uses jekyll to generate static files. For cart and order management it uses snipcart.

The website is hosted in [Gitlab Pages](https://altom.gitlab.io/altwalker/snipcart-jekyll-ecommerce-demo/) and its forked from [snipcart on github](https://github.com/snipcart/snipcart-jekyll-integration).

### Setup

For this Demo we used [geckodriver](https://github.com/mozilla/geckodriver) to launch the Firefox browser.


* Download [geckodriver](https://github.com/mozilla/geckodriver):

    After you download and extract the executable, make sure you set the path to the geckodriver executable in the `Path` variable to make other programs aware of its location.

    On Windows:

    ```
    $ set PATH=%PATH%;C:\bin\geckodriver
    ```

    On Linux/MacOS:

    ```
    $  ln -s /path/to/geckodriver /urs/local/bin/geckodriver
    ```

*  Clone the examples repositorie, with SSH:

    ```
    $ git clone git@gitlab.com:altom/altwalker/altwalker-examples.git
    ```

    Or with HTTPS:

    ```
    $ git clone https://gitlab.com/altom/altwalker/altwalker-examples.git
    ```

* Go into the ecommerce demo directory:

    ```
    $ cd altwalker-examples/ecommerce-snipcart-jekyll-example
    ```

* (__optional__) Create a python virtual enviroment:

    On Linux/MacOS:

    ```
    $ python3 -m venv .virtualenv
    $ source .virtualenv/bin/activate
    ```

    On Windows:

    ```
    $ python3 -m venv .virtualenv
    $ .virtualenv\Scripts\activate'
    ```

* Install the python dependencies:

    ```
    $ pip3 install -r requirements.txt
    ```

    Or:

    ```
    $ python3 -m pip install -r requirements.txt
    ```

### Run Tests

#### online

```
$ altwalker online -m models/default.json "random(edge_coverage(100))" tests
```

Walks randomly through the graph until all edges have been passed.

- starts GraphWalker REST service on default port 8887.
- initializes GraphWalker with `models/default.json` model and `random(edge_coverage(100))` generator stop condition.
- communicates with GraphWalker to get next step to be executed
- executes the test in `tests` package associated with the step

#### offline and walk

```
$ altwalker offline -m models/default.json "random(edge_coverage(100) && vertex_coverage(100))" -f steps.json
```

Generates a valid path throgh the test graph.
- runs graphwalker offline command to generate a list of valid steps through the graph.

```
altwalker walk tests ./steps.json
```

Walks on the steps in `./steps.json` file.
- reads steps from file
- executes, in the order from file, the tests in `tests` package associated with each step

#### check

```
altwalker check -m models/default.json "random(edge_coverage(100) && vertex_coverage(100))"
```

Checks the integity of the model.
- runs GraphWalker's check command
- runs AltwWalker's checks on json models interity


#### verify

```
$ altwalker verify -m models/default.json tests
```

Verifies that your model and tests are valid, and that all names referred in the model are implemented in `tests` package


### Modeling

![ecommerce altwalker model](_static/ecommerce-model.png)

We have modeled our ecommerce website as a directional graph. In our model file we specify wihch function is executed by AltWalker when we reach a vertex or an edge.

_Each vertex in the graph represents a state_ (e.g. `cart_not_empty`). This is where we put our asserts.

_Each edge in the graph represents an action_ (e.g. `add_to_cart`, `go_to_product_page`). This is where we put our page interaction code.


`models/default.json` contains __NavigationModel__ and __CheckoutModel__.
* __NavigationModel__ contains edges and models that verify homepage and product page behaviour.
* __CheckoutModel__ contains edges and models that verify cart checkout process.


### Shared States

__NavigationModel__ and __CheckoutModel__ are linked together by `cart_open_and_not_empty` and `homepage` vertices.

The `cart_open_and_not_empty` in NavigationModel has the same `sharedState` value as `cart_open_and_not_empty` in CheckoutModel.

The `homepage` in NavigationModel has the same `sharedState` value as `homepage` in CheckoutModel.

If GraphWalker reaches `cart_open_and_not_empty` in NavigationModel model, it will continue on `cart_open_and_not_empty` in CheckoutModel, and if reaches `hompage` from _CheckoutModel_ it will continue on with `homplage` from _NavigationModel_.

#### Actions and Guards

The `cart_open_and_not_empty` vertex from _NavigationModel_ has 4 edges linked into it. All of the 4 edges are guarded by:

```
"guard":"global.itemsInCart>0"
```

that means that GraphWalker will not generate a path that goes through the guarded edges unless `global.itemsInCart` is greater than 0. The `global.itemsInCart` variable is initialized at start in NavigationModel's actions:

```
"actions": ["global.itemsInCart=0;"]
```

and its updated in `add_to_cart_from_homepage`, `add_to_cart_from_product_page` and `e_place_order`, where it's increased by one each time one of the three edges is reached:

```
"actions": ["global.itemsInCart++;"]
```

This way we make sure that every time we reach `cart_open_and_not_empty` we have items in cart and we can jump to _CheckoutModel_.


### Tests

The tests can be found inside `tests` package. We use selenium and pypom to interact with the ecommerce website. The code that interacts with the page, is inside `tests/pages/` package.

Each model defined in `models/default.json` has an associated class in `tests/test.py`. `tests/test.py` contains `NavigationModel` and `CheckoutModel` classes.

During execution of tests, when the path reaches vertex with id `v_homepage` defined in NavigationModel, AltWalker will execute the method `tests/test.py::NavigationModel::homepage`.

__Further Reading / Useful Links__:
  * [Seleniun](https://docs.seleniumhq.org/)
  * [Selenium with python](https://selenium-python.readthedocs.io/)
  * [Python Page Object Model](https://pypom.readthedocs.io/en/latest/)