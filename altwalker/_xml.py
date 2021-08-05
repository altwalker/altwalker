"""Generates test results in the standard JUnit XML format for use with Jenkins and other build integration servers."""

import re
import sys
import datetime
import xml.dom.minidom
import xml.etree.ElementTree as ET
from collections import defaultdict

from altwalker._prettier import format_step_name


def xml_safe(value):
    """Replaces invalid `XML characters`_ with '?'.

    .. _XML characters:
       https://www.w3.org/TR/xml11/#charsets

    """

    # The characters defined in the following ranges are discouraged.
    # They are either control characters or permanently undefined Unicode characters:
    illegal_characters = [
        (0x00, 0x08),
        (0x0B, 0x1F),
        (0x7F, 0x84),
        (0x86, 0x9F),
        (0xD800, 0xDFFF),
        (0xFDD0, 0xFDDF),
        (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF),
        (0x2FFFE, 0x2FFFF),
        (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF),
        (0x5FFFE, 0x5FFFF),
        (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF),
        (0x8FFFE, 0x8FFFF),
        (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF),
        (0xBFFFE, 0xBFFFF),
        (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF),
        (0xEFFFE, 0xEFFFF),
        (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF),
    ]

    illegal_ranges = [
        "{}-{}".format(chr(low), chr(high)) for (low, high) in illegal_characters if low < sys.maxunicode
    ]

    illegal_regex = re.compile("[{}]".format("".join(illegal_ranges)))
    return illegal_regex.sub("?", value)


class TestCase:
    """A class that contains information about the execution of a single test case.

    Args:
        name (:obj:`str`): The display name of the test case.
        classname (:obj:`str`): The full name of the class.
        status (:obj:`str`): The status of the test case.
        stdout (:obj:`str`): The data written to ``stdout`` during the test execution.
        stderr (:obj:`str`): The data written to ``stderr`` during the test execution.
        assertions (:obj:`int`): The total number of asserts run in the test cases.
        timestamp (:obj:`str`): The time when the test case execution started.
        elapsed_seconds (:obj:`float`, :obj:`int`): The time, in fractional seconds, spent running the tests.
        filename (:obj:`str`): The full file name of the test case.
        line (:obj:`int`): The line number of the test case.

    """

    def __init__(self, name, classname=None, status=None, stdout=None, stderr=None, assertions=None, timestamp=None,
                 elapsed_seconds=None, filename=None, line=None):

        self.name = name
        self.classname = classname
        self.status = status

        self.stdout = stdout
        self.stderr = stderr

        self.assertions = assertions

        self.timestamp = timestamp
        self.elapsed_seconds = elapsed_seconds

        self.filename = filename
        self.line = line

        self.enabled = True
        self.errors = []
        self.failures = []
        self.skipped = []

    @property
    def is_enabled(self):
        """Returns ``True`` if this test case is enabled."""

        return self.enabled

    @property
    def is_error(self):
        """Returns ``True`` if this test case is an error."""

        return sum(1 for error in self.errors if error["message"] or error["output"]) > 0

    @property
    def is_failure(self):
        """Returns ``True`` if this test case is a failure."""

        return sum(1 for failure in self.failures if failure["message"] or failure["output"]) > 0

    @property
    def is_skipped(self):
        """Returns ``True`` if this test case has been skipped."""

        return len(self.skipped) > 0

    @property
    def attributes(self):
        attributes = {
            "name": str(self.name)
        }

        if self.assertions:
            attributes["assertions"] = str(self.assertions)
        if self.elapsed_seconds:
            attributes["time"] = str(self.elapsed_seconds)
        if self.timestamp:
            attributes["timestamp"] = str(self.timestamp)
        if self.classname:
            attributes["classname"] = str(self.classname)
        if self.status:
            attributes["status"] = str(self.status)
        if self.filename:
            attributes["file"] = str(self.filename)
        if self.line:
            attributes["line"] = str(self.line)

        return attributes

    def _error_xml(self, root_element):
        """Generates the error XML."""

        for error in self.errors:
            if error["message"] or error["output"]:
                attributes = {"type": "error"}

                if error["message"]:
                    attributes["message"] = str(error["message"])

                if error["type"]:
                    attributes["type"] = str(error["type"])

                error_element = ET.Element("error", attributes)

                if error["output"]:
                    error_element.text = str(error["output"])

                root_element.append(error_element)

    def _failure_xml(self, root_element):
        """Generates the failure XML."""

        for failure in self.failures:
            if failure["output"] or failure["message"]:
                attributes = {"type": "failure"}

                if failure["message"]:
                    attributes["message"] = str(failure["message"])

                if failure["type"]:
                    attributes["type"] = str(failure["type"])

                failure_element = ET.Element("failure", attributes)

                if failure["output"]:
                    failure_element.text = str(failure["output"])

                root_element.append(failure_element)

    def _skipped_xml(self, root_element):
        """Generates the skipped XML."""

        for skipped in self.skipped:
            attributes = {"type": "skipped"}

            if skipped["message"]:
                attributes["message"] = str(skipped["message"])

            skipped_element = ET.Element("skipped", attributes)

            if skipped["output"]:
                skipped_element.text = str(skipped["output"])

            root_element.append(skipped_element)

    def _xml(self, root_element):
        """Generates the test case XML."""

        element = ET.SubElement(root_element, "testcase", self.attributes)

        self._error_xml(element)
        self._failure_xml(element)
        self._skipped_xml(element)

        if self.stdout:
            stdout_element = ET.Element("system-out")
            stdout_element.text = str(self.stdout)
            element.append(stdout_element)

        if self.stderr:
            stderr_element = ET.Element("system-err")
            stderr_element.text = str(self.stderr)
            element.append(stderr_element)

    def add_error(self, message=None, output=None, error_type=None):
        """Adds an error message, output, or both to the test case.

        Args:
            message (:obj:`str`): The error message.
            output (:obj:`str`): The error output.
            error_type (:obj:`str`): The error type.

        """

        error = {
            "message": message,
            "output": output,
            "type": error_type
        }

        if message or output:
            self.errors.append(error)

    def add_failure(self, message=None, output=None, failure_type=None):
        """Adds a failure message, output, or both to the test case.

        Args:
            message (:obj:`str`): The failure message.
            output (:obj:`str`): The failure output.
            failure_type (:obj:`str`): The failure type.

        """

        failure = {
            "message": message,
            "output": output,
            "type": failure_type
        }

        if message or output:
            self.failures.append(failure)

    def add_skipped(self, message=None, output=None):
        """Adds a skipped message, output, or both to the test case.

        Args:
            message (:obj:`str`): The skip message.
            output (:obj:`str`): The skip output.

        """

        skipped = {
            "message": message,
            "output": output
        }

        if message or output:
            self.skipped.append(skipped)


class TestSuite:
    """A class that contains information about the execution of a single test suite.

    It also contains information about failures/errors related to the test suite.

    Args:
        test_cases (:obj:`list`): A list of :class:`~TestCase`.
        id (:obj:`str`): The id of the test suite.
        stdout (:obj:`str`): The data written to ``stdout`` during the test execution.
        stderr (:obj:`str`): The data written to ``stderr`` during the test execution.
        package (:obj:`str`): The package name of the test suite.
        hostname (:obj:`str`): The hostname of the test suite.
        filename (:obj:`str`): The full file name of the test suite.
        timestamp (:obj:`str`): The time when the test suite execution started.
        properties (:obj:`dict`): The test suite properties.

    """

    def __init__(self, name, test_cases, id=None, stdout=None, stderr=None, package=None, hostname=None,
                 filename=None, timestamp=None, properties=None):

        self.name = name
        self.test_cases = test_cases

        self.id = id
        self.stdout = stdout
        self.stderr = stderr
        self.package = package
        self.hostname = hostname
        self.filename = filename
        self.timestamp = timestamp
        self.properties = properties

    @property
    def assertions(self):
        return sum(int(test_case.assertions) for test_case in self.test_cases if test_case.assertions)

    @property
    def disabled(self):
        return sum(1 for test_case in self.test_cases if not test_case.is_enabled)

    @property
    def errors(self):
        return sum(1 for test_case in self.test_cases if test_case.is_error)

    @property
    def failures(self):
        return sum(1 for test_case in self.test_cases if test_case.is_failure)

    @property
    def skipped(self):
        return sum(1 for test_case in self.test_cases if test_case.is_skipped)

    @property
    def tests(self):
        return len(self.test_cases)

    @property
    def time(self):
        return sum(test_case.elapsed_seconds for test_case in self.test_cases if test_case.elapsed_seconds)

    @property
    def attributes(self):
        attributes = {
            "name": str(self.name)
        }

        if self.id:
            attributes["id"] = str(self.id)
        if self.timestamp:
            attributes["timestamp"] = str(self.timestamp)
        if self.hostname:
            attributes["hostname"] = str(self.hostname)
        if self.package:
            attributes["package"] = str(self.package)
        if self.filename:
            attributes["file"] = str(self.filename)

        attributes["tests"] = str(self.tests)
        attributes["assertions"] = str(self.assertions)
        attributes["disabled"] = str(self.disabled)
        attributes["errors"] = str(self.errors)
        attributes["failures"] = str(self.failures)
        attributes["skipped"] = str(self.skipped)
        attributes["time"] = str(self.time)

        return attributes

    def _properties_xml(self, root_element):
        """Generates the properties XML."""

        properties_element = ET.SubElement(root_element, "properties")

        for key, value in self.properties.items():
            attributes = {
                "name": str(key),
                "value": str(value)
            }

            ET.SubElement(properties_element, "property", attributes)

    def _xml(self):
        """Generates the XML document for the JUnit test suites."""

        xml_element = ET.Element("testsuite", self.attributes)

        if self.properties:
            self._properties_xml(xml_element)

        if self.stdout:
            stdout_element = ET.SubElement(xml_element, "system-out")
            stdout_element.text = str(self.stdout)

        if self.stderr:
            stderr_element = ET.SubElement(xml_element, "system-err")
            stderr_element.text = str(self.stderr)

        for test_case in self.test_cases:
            test_case._xml(xml_element)

        return xml_element


class TestReporter:
    """A test reporter class that can express test results in a JUnit XML report.

    Args:
        test_suites (:obj:`list`): A list of :class:`~TestSuite`.

    """

    def __init__(self, test_suites):
        self.test_suites = test_suites

    @property
    def attributes(self):
        attributes = defaultdict(int)

        for test_suit in self.test_suites:
            for key in ["disabled", "errors", "failures", "tests", "time"]:
                attributes[key] += getattr(test_suit, key)

        return attributes

    def _xml(self):
        """Generates the report XML."""

        xml_element = ET.Element("testsuites")

        for test_suit in self.test_suites:
            test_suit_xml = test_suit._xml()
            xml_element.append(test_suit_xml)

        for key, value in self.attributes.items():
            xml_element.set(key, str(value))

        return xml_element

    def to_string(self, prettyxml=True):
        """Generates a string representation of the JUnit XML report.

        Args:
            prettyxml (:obj:`bool`): Will generate a pretty-printed version of the document.

        """

        xml_element = self._xml()
        xml_string = ET.tostring(xml_element, encoding="unicode")
        xml_string = xml_safe(xml_string)

        if prettyxml:
            xml_string = xml.dom.minidom.parseString(xml_string)
            xml_string = xml_string.toprettyxml()

        return xml_string

    def write(self, filename="report.xml", prettyxml=True):
        """Writes the JUnit report to a file, as XML.

        Args:
            prettyxml (:obj:`bool`): Will generate a pretty-printed version of the document.

        """

        xml_string = self.to_string(prettyxml=prettyxml)

        with open(filename, "w") as fp:
            fp.write(xml_string)


class JUnitGenerator:
    """A class that can express an AltWalker run in a JUnit XML report."""

    def __init__(self):
        self.index = 0
        self.test_suite_timestamp = None
        self.test_case_timestamp = None

        self.test_suite = None
        self.test_cases = []

    def _format_content(self, content, title=None):
        if not content:
            return None

        if title:
            title = title.center(80, "-")
            return "{}\n\n{}".format(title, content)

        return content

    def to_string(self, prettyxml=True):
        """Generates a string representation of the JUnit XML report.

        Args:
            prettyxml (:obj:`bool`): Will generate a pretty-printed version of the document.

        """

        test_reporter = TestReporter([self.test_suite])
        return test_reporter.to_string(prettyxml=prettyxml)

    def write(self, filename, prettyxml=True):
        """Writes the JUnit report to a file, as XML.

        Args:
            prettyxml (:obj:`bool`): Will generate a pretty-printed version of the document.

        """

        test_reporter = TestReporter([self.test_suite])
        test_reporter.write(filename=filename, prettyxml=prettyxml)

    def start(self):
        self.test_suite_timestamp = datetime.datetime.now()

    def end(self, statistics=None):
        self.test_suite = TestSuite(
            "AltWalker Report", self.test_cases,
            timestamp=self.test_suite_timestamp,
            properties=statistics
        )

    def step_start(self):
        self.test_case_timestamp = datetime.datetime.now()

    def step_end(self, step, result):
        elapsed_seconds = datetime.datetime.now() - self.test_case_timestamp
        elapsed_seconds = elapsed_seconds.total_seconds()

        test_case = TestCase(
            "#{:05d} - {}".format(self.index, format_step_name(step)),
            classname=step.get("modelName"),
            stdout=self._format_content(result.get("output"), title="Output"),
            timestamp=self.test_case_timestamp,
            elapsed_seconds=elapsed_seconds
        )

        if result.get("error"):
            test_case.add_failure(
                message=self._format_content(result["error"].get("message"), title="Error"),
                output=self._format_content(result["error"].get("trace"), title="Trace")
            )

        self.test_cases.append(test_case)

        self.test_case_timestamp = None
        self.index += 1

    def error(self, step, message, trace=None):
        name = format_step_name(step) if step else "Unexpected Error."

        test_case = TestCase(
            "#{:05d} - {}".format(self.index, name),
            classname=step.get("modelName"),
        )

        test_case.add_error(
            message=self._format_content(message, title="Error"),
            output=self._format_content(trace, title="Trace")
        )

        self.test_cases.append(test_case)
        self.index += 1
