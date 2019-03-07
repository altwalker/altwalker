# Demo

## Altwalker ecommerce demo

In this example you will learn how to model your ecommerce website tests as a directional graph, how to use Actions, Guards and Shared State in your graph model. You will learn how to use altwalker's `online`, `offline`, `walk`, `check` and `verify` commands.

The tests are written in python with selenium and to python page object model. The ecommerce website beeing tested is written in markdown and uses jekyll to generate static files. For cart and order management it uses snipcart. 
The website is hosted in [Gitlab Pages](https://gitlab.com/altom/altwalker/snipcart-jekyll-ecommerce-demo) and its forked from [snipcart on github](https://github.com/snipcart/snipcart-jekyll-integration)


The code for this example is hosted at [https://gitlab.com/altom/altwalker/altwalker-examples](https://gitlab.com/altom/altwalker/altwalker-examples)


### Setup

For this Demo we used [geckodriver](https://github.com/mozilla/geckodriver) to launch the Firefox browser. After you download it, add the executable in the python parent folder. (e.g., C:\Python37)

```
git clone git@gitlab.com:altom/altwalker/altwalker-examples.git
cd altwalker-examples/ecommerce-snipcart-jekyll-example
python3 -m venv .virtualenv
source .virtualenv/bin/activate (use '.virtualenv\Scripts\activate' on Windows)
pip install -r requirements.txt
```

### Run tests

#### online

`altwalker online -m models/default.json "random(edge_coverage(100))" tests`

Altwalker walks randomly through the graph until all edges have been passed.

- starts graphwalker REST service on default port 8887.
- initializes graphwalker with `models/default.json` model and `random(edge_coverage(100))` generator stop condition.
- communicates with graphwalker to get next step to be executed
- executes the test in `tests` package associated with the step

---

#### offline and walk

`altwalker offline -m models/default.json "random(edge_coverage(100) && vertex_coverage(100))" -f steps.json`

Altwalker generates a valid path throgh the test graph.
- runs graphwalker offline command to generate a list of valid steps through the graph.

`altwalker walk tests ./steps.json`
Altwalker walks on the steps in `./steps.json` file.
- reads steps from file
- executes, in the order from file, the tests in `tests` package associated with each step

---

#### check

`altwalker check -m models/default.json "random(edge_coverage(100) && vertex_coverage(100))"`
Checks the integity of the model.
- runs graphwalker check command
- runs altwalker checks on json models interity


#### verify

`altwalker verify -m models/default.json  tests`

Altwalker verifies that your model and tests are valid, and that all names referred in the model are implemented in `tests` package


### Modeling

![ecommerce altwalker model](_static/ecommerce-model.png)

We have modeled our ecommerce website as a directional graph. In our model file we specify wihch function is executed by altwalker when we reach a vertex or an edge.

_Each vertex in the graph represents a state_ (e.g. cart_not_empty). This is where we put our asserts.

_Each edge in the graph represents an action_ (e.g. add_to_cart, go_to_product_page ). This is where we put our page interaction code.


`models/default.json` contains NavigationModel and CheckoutModel. 
NavigationModel contains edges and models that verify homepage and product page behaviour.
CheckoutModel contains edges and models that verify cart checkout process.


NavigationModel and CheckoutModel are linked together by cart_open_and_not_empty and homepage vertices. The cart_open_and_not_empty in NavigationModel has the same shared_state value as cart_open_and_not_empty in CheckoutModel. The homepage in NavigationModel has the same shared_state value as homepage in CheckoutModel. 

If graphwalker reaches cart_open_and_not_empty in NavigationModel model, it can continue on cart_open_and_not_empty in CheckoutModel.

cart_open_and_not_empty in NavigationModel has 4 edges linked into it. All of the 4 edges are guarded by `"guard":"global.itemsInCart>0"`. That means that graphwalker will not generate a path that goes through the guarded edges unless `global.itemsInCart>0`.  `global.itemsInCart` is initialized at start in NavigationModel, and its updated in `add_to_cart_from_homepage`, `add_to_cart_from_product_page` and `e_place_order`. This way we make sure that every time we reach cart_open_and_not_empty we have items in cart and we can jump to CheckoutModel.

```
"actions": ["global.itemsInCart=0;"]
"actions": ["global.itemsInCart++;"]
"guard": "global.itemsInCart>0"
```

### Tests

The tests can be found inside `tests` package. We use selenium and pypom to interact with the ecommerce website. The code that interacts with the page, inside `test/pages`. 

Each model defined in `models/default.json` has an associated class in `tests/test.py`. `tests/test.py` contains `NavigationModel` and `CheckoutModel` classes. 

During execution of tests, when the path reaches vertex with id `v_homepage` defined in NavigationModel, altwalker will execute the method `tests/test.py::NavigationModel::homepage`
