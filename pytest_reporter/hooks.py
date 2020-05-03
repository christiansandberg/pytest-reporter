import pytest


def pytest_reporter_template_dirs(config):
    pass


def pytest_reporter_context(context, config):
    pass


@pytest.hookspec(firstresult=True)
def pytest_reporter_render(template_name, dirs, context):
    pass


def pytest_reporter_save(config):
    pass


def pytest_reporter_finish(path, context, config):
    pass
