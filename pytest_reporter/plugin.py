from pathlib import Path
import logging

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--report-path",
        action="append",
        default=["report.html"],
        help="path to report output.",
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
        default=["default/index.html"],
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
        "test_items": [],
    }
    if config.getoption("--report-path") and not is_slave:
        from .engines import jinja2, mako
        from .templates.default import conftest as default
        config._reporter = ReportGenerator(config)
        config.pluginmanager.register(config._reporter)
        config.pluginmanager.register(jinja2)
        config.pluginmanager.register(mako)
        config.pluginmanager.register(default)


def pytest_reporter_context(config):
    return config.template_context


class TestRun:
    def __init__(self, item):
        self.item = item
        self.phases = []
        self.category = ""
        self.letter = ""
        self.word = ""
        self.style = {}

    def append_phase(self, phase):
        self.phases.append(phase)
        if phase.letter or phase.word:
            self.category = phase.category
            self.letter = phase.letter
            self.word = phase.word
            self.style = phase.style


class TestPhase:
    def __init__(self, call, report, log_records, config):
        self.call = call
        self.report = report
        self.log_records = log_records
        res = config.hook.pytest_report_teststatus(report=report, config=config)
        self.category, self.letter, self.word = res
        if isinstance(self.word, tuple):
            self.word, self.style = self.word
        else:
            self.style = {}


class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self._active = None
        self._log_handler = LogHandler()

    def pytest_sessionstart(self, session):
        logging.getLogger().addHandler(self._log_handler)

    def pytest_runtest_protocol(self, item):
        self._active = TestRun(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        log_records = self._log_handler.pop_records()
        phase = TestPhase(call, report, log_records, self.config)
        self._active.append_phase(phase)

    def pytest_runtest_logfinish(self):
        self.config.template_context["test_items"].append(self._active)

    def pytest_sessionfinish(self, session):
        config = session.config
        logging.getLogger().removeHandler(self._log_handler)
        # Create a template environment or template lookup object
        dirs = config.getoption("--template-dir")
        env = config.hook.pytest_reporter_make_env(template_dirs=dirs, config=config)
        # Allow modification
        config.hook.pytest_reporter_modify_env(env=env, config=config)
        # Generate context
        contexts = config.hook.pytest_reporter_context(config=config)
        ctx = {}
        for context in contexts:
            ctx.update(context)
        for template, path in zip(
            config.getoption("--template"), config.getoption("--report-path")
        ):
            content = config.hook.pytest_reporter_render(
                env=env, template=template, context=ctx
            )
            # Save content to file
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            config.hook.pytest_reporter_finish(
                path=path, env=env, context=ctx, config=config
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
