import traceback

from altwalker.reporter import Reporter


class Walker:
    """Coordinates the execution of a test asking a ``Planner`` for the next step,
    executing the step using an ``Executor``, if needed passing a ``dict`` object
    to the test code, and reporting the progress using a ``Reporter``.
    """

    def __init__(self, planner, executor, reporter):
        self._planner = planner
        self._executor = executor
        self._reporter = reporter

        self._status = None

        # a list of models to tearDown
        self._models = []

    def __iter__(self):
        self._reporter.start()
        self._planner.restart()
        self._executor.reset()
        self._status = self._setUpRun()

        # if setUpRun failed stop
        if not self._status:
            return

        while self._planner.has_next() and self._status:
            step = self._planner.get_next()

            if step["modelName"] not in self._models:
                self._status = self._setUpModel(step["modelName"])

                # if setUpModel failed stop executing steps
                if not self._status:
                    break

            self._status = self._run_step(step)
            step["status"] = self._status

            yield step

        status = self._tearDownModels()
        self._status = self._status & status

        status = self._tearDownRun()
        self._status = self._status & status

        self._reporter.end()

    @property
    def status(self):
        """The status of the current run."""

        return self._status

    def _setUpRun(self):
        step = {
            "type": "fixture",
            "name": "setUpRun"
        }

        return self._run_step(step, optional=True)

    def _tearDownRun(self):
        step = {
            "type": "fixture",
            "name": "tearDownRun"
        }

        return self._run_step(step, optional=True)

    def _setUpModel(self, model):
        step = {
            "type": "fixture",
            "name": "setUpModel",
            "modelName": model
        }

        status = self._run_step(step, optional=True)

        if status:
            self._models.append(model)

        return status

    def _tearDownModel(self, model):
        step = {
            "type": "fixture",
            "name": "tearDownModel",
            "modelName": model
        }

        return self._run_step(step, optional=True)

    def _tearDownModels(self):
        status = True

        for model in self._models:
            temp = self._tearDownModel(model)
            status = status and temp

        self._models = []

        return status

    def _update_data(self, data_before, data_after):
        if not data_after:
            return

        for key, value in data_after.items():
            if key not in data_before or data_before[key] != value:
                self._planner.set_data(key, value)

    def _execute_step(self, model, name):
        data_before = self._planner.get_data()

        result = self._executor.execute_step(model, name, data_before)
        data_after = result.get("data", None)

        self._update_data(data_before, data_after)

        return result

    def _run_step(self, step, optional=False):
        model = step.get("modelName", None)
        name = step.get("name")

        if not self._executor.has_step(model, name):
            if not optional:
                self._planner.fail(step, "Step not found.")

                self._reporter.step_status(step, failure=True)
                self._reporter.error("Step not found.")

            return optional

        try:
            self._reporter.step_start(step)

            result = self._execute_step(model, name)

            error = result.get("error", None)
            output = result["output"]

            self._reporter.step_status(step, output=output, failure=error is not None)

            if error:
                self._planner.fail(step, error["message"])
                self._reporter.error(error["message"], trace=error["trace"])

            return error is None
        except Exception as e:
            self._planner.fail(step, str(e))

            self._reporter.step_status(step, failure=True)
            self._reporter.error(str(e), trace=str(traceback.format_exc()))

            return False

    def run(self):
        """Run tests."""

        for _ in self:
            pass

        return self._status


def create_walker(planner, executor, reporter=None):
    """Create a Walker object, and if no ``reporter`` is provided
    initialize it with the default options.
    """

    if not reporter:
        reporter = Reporter()

    return Walker(planner, executor, reporter)
