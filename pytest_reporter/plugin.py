from pathlib import Path
import logging
import time

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
        "--template-engine",
        choices=["jinja2", "mako"],
        default="jinja2",
        help="template engine to use.",
    )
    group.addoption(
        "--template",
        action="append",
        default=[],
        help="path to report template relative to --template-dir.",
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
    is_slave = hasattr(config, "slaveinput")
    config.template_context = {
        "config": config,
        "test_runs": [],
    }
    if config.getoption("--report") and not is_slave:
        from .engines import jinja2, mako

        config._reporter = ReportGenerator(config)
        config.pluginmanager.register(config._reporter)
        config.pluginmanager.register(jinja2)
        config.pluginmanager.register(mako)


@pytest.hookimpl(tryfirst=True)
def pytest_reporter_template_dir(config):
    return config.getoption("--template-dir")


def pytest_reporter_context(context, config):
    """Add status to test runs and phases."""
    for run in context["test_runs"]:
        for phase in run["phases"]:
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
                run["status"] = phase["status"]


@pytest.fixture(scope="session")
def session_context(pytestconfig):
    """Report template context for session."""
    return pytestconfig.template_context


@pytest.fixture(scope="function")
def function_context(pytestconfig):
    """Report template context for the current function."""
    return pytestconfig._reporter._active_log


class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self._active_item = None
        self._active_log = None
        self._log_handler = LogHandler()

    def pytest_sessionstart(self, session):
        self.config.template_context["started"] = time.time()
        logging.getLogger().addHandler(self._log_handler)

    def pytest_runtest_protocol(self, item):
        self._active_item = item

    def pytest_runtest_logstart(self):
        self._active_log = {
            "item": self._active_item,
            "phases": [],
        }
        self.config.template_context["test_runs"].append(self._active_log)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        phase = {}
        self._active_log["phases"].append(phase)
        phase["call"] = call
        outcome = yield
        report = outcome.get_result()
        phase["report"] = report
        phase["log_records"] = self._log_handler.pop_records()

    def pytest_sessionfinish(self, session):
        config = session.config
        config.template_context["ended"] = time.time()
        logging.getLogger().removeHandler(self._log_handler)
        # Create a template environment or template lookup object
        template_dirs = []
        for dirs in config.hook.pytest_reporter_template_dir(config=config):
            if isinstance(dirs, list):
                template_dirs.extend(dirs)
            else:
                template_dirs.append(dirs)
        env = config.hook.pytest_reporter_make_env(
            template_dirs=template_dirs, config=config
        )
        # Allow modification
        config.hook.pytest_reporter_modify_env(env=env, config=config)
        # Generate context
        context = config.template_context
        config.hook.pytest_reporter_context(context=context, config=config)
        for template, path in zip(
            config.getoption("--template"), config.getoption("--report")
        ):
            content = config.hook.pytest_reporter_render(
                env=env, template=template, context=context
            )
            # Save content to file
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            config.hook.pytest_reporter_finish(
                path=path, env=env, context=context, config=config
            )


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
