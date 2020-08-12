from pathlib import Path
import logging
import time
import warnings
from itertools import chain

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("report generation")
    group.addoption(
        "--report",
        action="append",
        default=[],
        help="path to report output (combined with --template).",
    )
    group.addoption(
        "--template",
        action="append",
        default=[],
        help="name or path to report template relative to --template-dir.",
    )
    group.addoption(
        "--template-dir",
        action="append",
        default=["."],
        help="path to template directory (multiple allowed).",
    )


def pytest_addhooks(pluginmanager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config):
    is_worker = hasattr(config, "workerinput")
    config.template_context = {
        "config": config,
        "tests": [],
        "warnings": [],
    }
    if config.getoption("--report") and not is_worker:
        config._reporter = ReportGenerator(config)
        config.pluginmanager.register(config._reporter)


@pytest.hookimpl(tryfirst=True)
def pytest_reporter_template_dirs(config):
    return config.getoption("--template-dir")


def pytest_reporter_context(context, config):
    """Add status to test runs and phases."""
    for test in context["tests"]:
        for phase in test["phases"]:
            category, letter, word = config.hook.pytest_report_teststatus(
                report=phase["report"], config=config
            )
            if isinstance(word, tuple):
                word, style = word
            else:
                style = {}
            phase["status"] = {
                "category": category,
                "letter": letter,
                "word": word,
                "style": style,
            }
            if letter or word:
                test["status"] = phase["status"]


@pytest.fixture(scope="session")
def template_context(pytestconfig):
    """Report template context for session."""
    return pytestconfig.template_context


@pytest.fixture(scope="function")
def function_context(pytestconfig):
    """Report template context for the current function."""
    if hasattr(pytestconfig, "_reporter"):
        return pytestconfig._reporter._active_test
    else:
        return {}


class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.context = config.template_context
        self._loaders = []
        self._active_item = None
        self._active_test = None
        self._log_handler = LogHandler()
        self._reports = set()

    def pytest_sessionstart(self, session):
        self.context["session"] = session
        self.context["started"] = time.time()
        logging.getLogger().addHandler(self._log_handler)

    def pytest_runtest_protocol(self, item):
        self._active_item = item

    def pytest_runtest_logstart(self):
        self._active_test = {
            "item": self._active_item,
            "phases": [],
            "status": {
                "category": "unknown",
                "letter": "?",
                "word": "UNKNOWN",
                "style": {},
            },
        }

    def pytest_runtest_logfinish(self):
        self.context["tests"].append(self._active_test)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        phase = {"call": call}
        outcome = yield
        report = outcome.get_result()
        phase["report"] = report
        phase["log_records"] = self._log_handler.pop_records()
        self._active_test["phases"].append(phase)

    def pytest_warning_captured(self, warning_message):
        self.context["warnings"].append(warning_message)

    def pytest_sessionfinish(self, session):
        self.context["ended"] = time.time()
        logging.getLogger().removeHandler(self._log_handler)
        self.config.hook.pytest_reporter_save(config=self.config)

    def pytest_reporter_save(self, config):
        # Create a list of all directories that may contain templates
        dirs_list = config.hook.pytest_reporter_template_dirs(config=config)
        dirs = list(chain.from_iterable(dirs_list))
        config.hook.pytest_reporter_loader(dirs=dirs, config=config)
        config.hook.pytest_reporter_context(context=self.context, config=config)
        for name, path in zip(
            config.getoption("--template"), config.getoption("--report")
        ):
            content = config.hook.pytest_reporter_render(
                template_name=name, dirs=dirs, context=self.context
            )
            if content is None:
                warnings.warn("No template found with name '%s'" % name)
                continue
            # Save content to file
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            config.hook.pytest_reporter_finish(
                path=target, context=self.context, config=config
            )
            self._reports.add(target)

    def pytest_terminal_summary(self, terminalreporter):
        for report in self._reports:
            terminalreporter.write_sep("-", "generated report: %s" % report.resolve())


class LogHandler(logging.Handler):
    def __init__(self):
        self._buffer = []
        super().__init__()

    def emit(self, record):
        self._buffer.append(record)

    def pop_records(self):
        records = self._buffer
        self._buffer = []
        return records
