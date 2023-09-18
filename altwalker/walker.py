#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

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
        planner (Planner): The test planner responsible for determining the next step.
        executor (Executor): The test executor responsible for executing steps.
        reporter (Reporter): The reporter to record and report test progress.
    """

    def __init__(self, planner, executor, reporter):
        self._planner = planner
        self._executor = executor
        self._reporter = reporter
        self._status = None
        self._models = list()  # a list of models to tearDown

    def __iter__(self):
        """Iterate over the test steps and execute them.

        Yields:
            dict: A dictionary representing each executed test step.
        """

        self._reporter.start()
        self._planner.restart()
        self._executor.reset()
        self._status = self._setup_run()

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
                self._status = self._setup_model(step["modelName"])

                # If setUpModel failed stop the run
                if not self._status:
                    break

            self._status = self._run_step(step)
            step["status"] = self._status

            yield step

        status = self._teardown_models()
        self._status = self._status & status

        status = self._teardown_run()
        self._status = self._status & status

        self._reporter.end(statistics=self._planner.get_statistics(), status=self._status)

    @property
    def status(self):
        """The status of the current test run.

        Returns:
            bool: ``True`` if the test run is successful, ``False`` otherwise.
        """

        return self._status

    def _update_data(self, data_before, data_after):
        """Update test data after step execution.

        Args:
            data_before (dict): Data before step execution.
            data_after (dict): Data after step execution.
        """

        if not data_after or data_before == data_after:
            return

        for key, value in data_after.items():
            if key not in data_before or data_before[key] != value:
                self._planner.set_data(key, value)

    def _execute_step(self, step, current_step=None):
        """Execute a test step.

        Args:
            step (dict): The test step to execute.
            current_step (dict, optional): The current test step being executed (default: None).

        Returns:
            bool: True if the step is executed successfully, False otherwise.
        """

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
        """Execute a test fixture.

        Args:
            fixture_name (str): The name of the fixture to execute.
            model_name (str, optional): The name of the test model (default: None).
            current_step (dict, optional): The current test step being executed (default: None).

        Returns:
            bool: ``True`` if the fixture is executed successfully, ``False`` otherwise.
        """

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
        """Execute a test step.

        Args:
            step (dict): The test step to execute.

        Returns:
            bool: ``True`` if the step is executed successfully, ``False`` otherwise.
        """

        if not self._executor.has_step(step.get("modelName"), step.get("name")):
            self._planner.fail("Step not found.")
            self._reporter.error(
                step,
                "Step not found.\nUse the 'verify' command to validate the test code against the model(s)."
            )
            return False

        try:
            return self._execute_step(step, current_step=step)
        except Exception as e:
            self._planner.fail(str(e))
            self._reporter.error(step, str(e), trace=str(traceback.format_exc()))

            return False

    def _run_step(self, step):
        """Execute a test step along with all associated fixtures (e.g., 'beforeStep', 'afterStep').

        Args:
            step (dict): The test step to execute.

        Returns:
            bool: ``True`` the step and its fixtures were executed successfully; otherwise ``False``.
        """

        if not step.get("name"):
            # Skip vertices and edges without names
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

    def _setup_run(self):
        """Setup a test run before execution.

        Returns:
            bool: ``True`` if the fixture is executed successfully, ``False`` otherwise.
        """

        return self._execute_fixture("setUpRun")

    def _teardown_run(self):
        """Teardown a test run after execution.

        Returns:
            bool: ``True`` if the fixture is executed successfully, ``False`` otherwise.
        """

        return self._execute_fixture("tearDownRun")

    def _setup_model(self, model_name):
        """Setup a test model before execution.

        Args:
            model_name (str): The name of the test model to set up.

        Returns:
            bool: ``True`` if model setup is successful, ``False`` otherwise.
        """

        status = self._execute_fixture("setUpModel", model_name=model_name)

        if status:
            self._models.append(model_name)

        return status

    def _teardown_model(self, model_name):
        """Teardown a test model after execution.

        Args:
            model_name (str): The name of the test model to set up.

        Returns:
            bool: ``True`` if model teardown is successful, ``False`` otherwise.
        """

        return self._execute_fixture("tearDownModel", model_name=model_name)

    def _teardown_models(self):
        """Teardown all test models after execution.

        Returns:
            bool: ``True`` if teardown is successful for all models, ``False`` otherwise.
        """

        status = True

        for model_name in self._models:
            temp = self._teardown_model(model_name)
            status = status and temp

        self._models = []

        return status

    def run(self):
        """Run tests.

        Returns:
            bool: ``True`` if all tests are executed successfully, ``False`` otherwise.
        """

        for _ in self:
            pass

        return self._status


def create_walker(planner, executor, reporter=None):
    """Create a Walker object, and if no ``reporter`` is provided initialize it with the default options.

    Args:
        planner (Planner): The test planner responsible for determining the next step.
        executor (Executor): The test executor responsible for executing steps.
        reporter (Reporter, optional): The reporter to record and report test progress (default: None).

    Returns:
        Walker: An instance of the Walker class.
    """

    if not reporter:
        reporter = Reporter()

    return Walker(planner, executor, reporter)
