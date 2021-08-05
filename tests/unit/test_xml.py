import os
import datetime

import pytest

import altwalker._xml as xml


VALID_CHARS = [0x9, 0xA, 0x20]
INVALID_CHARS = [0x1, 0xB, 0xC, 0xE, 0x00, 0x19, 0xD800, 0xDFFF, 0xFFFE, 0x0FFFF]


@pytest.mark.parametrize(
    "string, expected", [
        *[(chr(x), chr(x)) for x in VALID_CHARS],
        *[(chr(x), "?") for x in INVALID_CHARS]
    ]
)
def test_xml_save(string, expected):
    assert xml.xml_safe(string) == expected


class TestTestCase:

    def test_is_enabled(self):
        test_case = xml.TestCase("Test Case #1")
        assert test_case.is_enabled

    @pytest.mark.parametrize(
        "errors, expected", [
            ([], False),
            ([{}], False),
            ([{"message": "Error."}], True),
            ([{"output": "Error."}], True),
            ([{"message": "Error."}, {"output": "Error."}], True),
        ]
    )
    def test_is_error(self, errors, expected):
        test_case = xml.TestCase("Test Case #1")

        for error in errors:
            test_case.add_error(**error)

        assert test_case.is_error == expected

    @pytest.mark.parametrize(
        "failures, expected", [
            ([], False),
            ([{}], False),
            ([{"message": "Fail."}], True),
            ([{"output": "Fail."}], True),
            ([{"message": "Fail."}, {"output": "Fail."}], True),
        ]
    )
    def test_is_failure(self, failures, expected):
        test_case = xml.TestCase("Test Case #1")

        for failure in failures:
            test_case.add_failure(**failure)

        assert test_case.is_failure == expected

    @pytest.mark.parametrize(
        "skips, expected", [
            ([], False),
            ([{}], False),
            ([{"message": "Skip."}], True),
            ([{"output": "Skip."}], True),
            ([{"message": "Skip."}, {"output": "Skip."}], True),
        ]
    )
    def test_is_skipped(self, skips, expected):
        test_case = xml.TestCase("Test Case #1")

        for skip in skips:
            test_case.add_skipped(**skip)

        assert test_case.is_skipped == expected

    def test_empty_attributes(self):
        test_case = xml.TestCase("Test Case #1")
        expected = {
            "name": "Test Case #1"
        }

        assert test_case.attributes == expected

    def test_attributes(self):
        test_case = xml.TestCase(
            "Test Case #1",
            status="Failed",
            classname="TestModel",
            filename="test.py",
            line=24,
            assertions=3,
            elapsed_seconds=10,
            timestamp=datetime.datetime(2020, 8, 24)
        )

        expected = {
            "name": "Test Case #1",
            "status": "Failed",
            "classname": "TestModel",
            "file": "test.py",
            "line": "24",
            "assertions": "3",
            "time": "10",
            "timestamp": "2020-08-24 00:00:00"
        }

        assert test_case.attributes == expected


class TestTestSuite:

    def test_assetions(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x), assertions=x) for x in range(10)
        ]
        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.assertions == 45

    def test_disabled(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]
        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.disabled == 0

    def test_errors(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]

        for test_case in test_cases:
            test_case.add_error(message="Error Message.")

        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.errors == 10

    def test_failure(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]

        for test_case in test_cases:
            test_case.add_failure(message="Fail Message.")

        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.failures == 10

    def test_skipped(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]

        for test_case in test_cases:
            test_case.add_skipped(message="Skip Message.")

        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.skipped == 10

    def test_tests(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]
        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.tests == 10

    def test_time(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x), elapsed_seconds=x) for x in range(10)
        ]
        test_suite = xml.TestSuite("Test Suite", test_cases)

        assert test_suite.time == 45

    def test_empty_attributes(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x), assertions=x, elapsed_seconds=x) for x in range(10)
        ]
        test_suite = xml.TestSuite("Test Suite", test_cases)

        for test_case in test_cases:
            test_case.add_error(message="Error Message.")
            test_case.add_failure(message="Fail Message.")
            test_case.add_skipped(message="Skip Message.")

        expected = {
            "name": "Test Suite",
            "assertions": "45",
            "disabled": "0",
            "errors": "10",
            "failures": "10",
            "skipped": "10",
            "tests": "10",
            "time": "45"
        }

        assert test_suite.attributes == expected

    def test_attributes(self):
        test_suite = xml.TestSuite(
            "Test Suite", [],
            id="ID #0",
            timestamp=datetime.datetime(2020, 8, 24),
            hostname="localhost",
            package="tests",
            filename="test.py"
        )

        expected = {
            "name": "Test Suite",
            "id": "ID #0",
            "timestamp": "2020-08-24 00:00:00",
            "hostname": "localhost",
            "package": "tests",
            "file": "test.py",
            "assertions": "0",
            "disabled": "0",
            "errors": "0",
            "failures": "0",
            "skipped": "0",
            "tests": "0",
            "time": "0"
        }

        assert test_suite.attributes == expected


class TestTestReporter:

    def test_attributes(self):
        test_cases = [
            xml.TestCase("Test Case #{}".format(x)) for x in range(10)
        ]

        for test_case in test_cases:
            test_case.add_error(message="Error Message.")
            test_case.add_failure(message="Fail Message.")
            test_case.add_skipped(message="Skip Message.")

        test_suites = [
            xml.TestSuite("Test Suite #{}".format(x), test_cases) for x in range(10)
        ]
        test_reporter = xml.TestReporter(test_suites)

        expected = {
            "disabled": 0,
            "errors": 100,
            "failures": 100,
            "tests": 100,
            "time": 0
        }

        assert test_reporter.attributes == expected


class TestJUnitGenerator:

    @pytest.mark.parametrize(
        "content, title, expected", [
            ("", None, None),
            ("", "Output", None),
            ("Text", None, "Text"),
            ("Text", "", "Text"),
            ("Text", "Output", (37 * "-") + "Output" + (37 * "-") + "\n\nText")
        ]
    )
    def test_format_content(self, content, title, expected):
        generator = xml.JUnitGenerator()
        result = generator._format_content(content, title=title)

        assert result == expected

    @pytest.mark.parametrize("prettyxml", [True, False])
    def test_to_string(self, prettyxml):
        generator = xml.JUnitGenerator()

        generator.start()
        generator.end()

        assert generator.to_string(prettyxml=prettyxml) != ""

    @pytest.mark.parametrize("prettyxml", [True, False])
    def test_write(self, tmpdir, prettyxml):
        filename = os.path.join(str(tmpdir), "report.xml")
        generator = xml.JUnitGenerator()

        generator.start()
        generator.end()
        generator.write(filename=filename, prettyxml=prettyxml)

        with open(filename) as fp:
            data = fp.read()

        assert data != ""
