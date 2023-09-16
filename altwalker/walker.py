import logging
import traceback

from altwalker.exceptions import GraphWalkerException
from altwalker.reporter import Reporter

logger = logging.getLogger(__name__)


class Walker:
    """Coordinates the execution of a test asking a ``Planner`` for the next step,
    executing the step using an ``Executor``, if needed passing a ``dict`` object
    to the test code, and reporting the progress using a ``Reporter``.

    Args:

    """

    def __init__(self, planner, executor, reporter):
        self._planner = planner
        self._executor = executor
        self._reporter = reporter
        self._status = None
        self._models = list()  # a list of models to tearDown

    def __iter__(self):
        self._reporter.start()
        self._planner.restart()
        self._executor.reset()
        self._status = self._setUpRun()

        # if setUpRun failed stop
        if not self._status:
            self._reporter.end(statistics=self._planner.get_statistics(), status=self._status)
            return

        while self._status and self._planner.has_next():
            try:
                step = self._planner.get_next()
            except GraphWalkerException as ex:
                self._reporter.error(None, str(ex))
                self._status = False
                break

            if step["modelName"] not in self._models:
                self._status = self._setUpModel(step["modelName"])

                # if setUpModel failed stop executing steps
                if not self._status:
                    break

            if not step.get("name"):
                continue

            self._status = self._run_step(step)
            step["status"] = self._status

            yield step

        status = self._tearDownModels()
        self._status = self._status & status

        status = self._tearDownRun()
        self._status = self._status & status

        self._reporter.end(statistics=self._planner.get_statistics(), status=self.status)

    @property
    def status(self):
        """The status of the current run."""

        return self._status

    def _update_data(self, data_before, data_after):
        if not data_after:
            return

        for key, value in data_after.items():
            if key not in data_before or data_after[key] != value:
                self._planner.set_data(key, value)

    def _execute_step(self, step, current_step=None):
        if not current_step:
            current_step = step

        data_before = self._planner.get_data()

        self._reporter.step_start(step)
        step_result = self._executor.execute_step(
            step.get("modelName"),
            step.get("name"),
            data=data_before,
            step=current_step
        )
        self._reporter.step_end(step, step_result)

        data_after = step_result.get("data")
        self._update_data(data_before, data_after)

        error = step_result.get("error")
        if error:
            self._planner.fail(error["message"])

        return error is None

    def _execute_fixture(self, fixture_name, model_name=None, current_step=None):
        """Run a fixture."""

        fixture = {"type": "fixture", "name": fixture_name}
        if model_name:
            fixture["modelName"] = model_name

        if not self._executor.has_step(fixture.get("modelName"), fixture.get("name")):
            return True

        try:
            return self._execute_step(fixture, current_step=current_step)
        except Exception as e:
            self._planner.fail(str(e))
            self._reporter.error(fixture, str(e), trace=str(traceback.format_exc()))

            return False

    def _execute_test(self, step):
        try:
            return self._execute_step(step, current_step=step)
        except Exception as e:
            self._planner.fail(str(e))
            self._reporter.error(step, str(e), trace=str(traceback.format_exc()))

            return False

    def _run_step(self, step):
        if not step.get("name"):
            return True

        fixture_status = self._execute_fixture("beforeStep", current_step=step)
        if not fixture_status:
            return False

        fixture_status = self._execute_fixture("beforeStep", model_name=step["modelName"], current_step=step)
        if not fixture_status:
            return False

        step_status = self._execute_test(step)
        step["status"] = step_status

        fixture_status = self._execute_fixture("afterStep", model_name=step["modelName"], current_step=step)
        if not fixture_status:
            return False

        fixture_status = self._execute_fixture("afterStep", current_step=step)
        if not fixture_status:
            return False

        return step_status

    def _setUpRun(self):
        return self._execute_fixture("setUpRun")

    def _tearDownRun(self):
        return self._execute_fixture("tearDownRun")

    def _setUpModel(self, model_name):
        status = self._execute_fixture("setUpModel", model_name=model_name)

        if status:
            self._models.append(model_name)

        return status

    def _tearDownModel(self, model_name):
        return self._execute_fixture("tearDownModel", model_name=model_name)

    def _tearDownModels(self):
        status = True

        for model_name in self._models:
            temp = self._tearDownModel(model_name)
            status = status and temp

        self._models = []

        return status

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
