import pytest
import _pytest


pytest_plugins = ["pytester"]


@pytest.fixture
def template(testdir):
    testdir.makeconftest(
        """
        import json
        import pytest

        def pytest_reporter_render(template_name, dirs, context):
            return template_name
    """
    )


@pytest.fixture
def get_context(testdir, template):
    def _get_context():
        hooks = testdir.inline_run("--template=dummy.txt", "--report=report.txt")
        return hooks.getcall("pytest_reporter_render").context
    return _get_context


def test_file_is_saved(testdir, template):
    testdir.makepyfile("def test_pass(): pass")
    testdir.runpytest("--template=dummy.txt", "--report=report.txt")
    report = testdir.tmpdir.join("report.txt")
    assert report.read() == "dummy.txt"


def test_top_level_context(testdir, get_context):
    testdir.makepyfile("def test_pass(): pass")
    context = get_context()

    assert isinstance(context["config"], _pytest.config.Config)
    assert isinstance(context["session"], _pytest.main.Session)
    assert isinstance(context["started"], float)
    assert isinstance(context["ended"], float)


def test_tests(testdir, get_context):
    testdir.makepyfile("def test_pass(): pass")
    context = get_context()

    assert "tests" in context
    assert len(context["tests"]) == 1
    test = context["tests"][0]

    assert "item" in test
    assert isinstance(test["item"], _pytest.nodes.Item)
    assert test["item"].name == "test_pass"

    assert "phases" in test
    assert len(test["phases"]) == 3
    for phase, when in zip(test["phases"], ["setup", "call", "teardown"]):
        assert "call" in phase
        assert "report" in phase
        assert "log_records" in phase
        assert "status" in phase

        assert phase["call"].when == when
        assert phase["report"].when == when
        assert phase["report"].outcome == "passed"


def test_status(testdir, get_context):
    testdir.makepyfile(
        """
        def test_pass(): assert True
        def test_fail(): assert False
    """
    )
    context = get_context()
    passed, failed = context["tests"]

    assert passed["status"]["category"] == "passed"
    assert passed["status"]["letter"] == "."
    assert passed["status"]["word"] == "PASSED"
    assert isinstance(passed["status"]["style"], dict)

    assert failed["status"]["category"] == "failed"
    assert failed["status"]["letter"] == "F"
    assert failed["status"]["word"] == "FAILED"
    assert isinstance(failed["status"]["style"], dict)

    # setup
    assert passed["phases"][0]["status"]["category"] == ""
    assert passed["phases"][0]["status"]["letter"] == ""
    assert passed["phases"][0]["status"]["word"] == ""
    assert passed["phases"][0]["status"]["style"] == {}
    # call
    assert passed["phases"][1]["status"]["category"] == "passed"
    assert passed["phases"][1]["status"]["letter"] == "."
    assert passed["phases"][1]["status"]["word"] == "PASSED"
    # teardown
    assert passed["phases"][2]["status"]["category"] == ""
    assert passed["phases"][2]["status"]["letter"] == ""
    assert passed["phases"][2]["status"]["word"] == ""
    assert passed["phases"][2]["status"]["style"] == {}

    # setup
    assert failed["phases"][0]["status"]["category"] == ""
    assert failed["phases"][0]["status"]["letter"] == ""
    assert failed["phases"][0]["status"]["word"] == ""
    assert failed["phases"][0]["status"]["style"] == {}
    # call
    assert failed["phases"][1]["status"]["category"] == "failed"
    assert failed["phases"][1]["status"]["letter"] == "F"
    assert failed["phases"][1]["status"]["word"] == "FAILED"
    # teardown
    assert failed["phases"][2]["status"]["category"] == ""
    assert failed["phases"][2]["status"]["letter"] == ""
    assert failed["phases"][2]["status"]["word"] == ""
    assert failed["phases"][2]["status"]["style"] == {}
