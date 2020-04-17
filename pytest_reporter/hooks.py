import pytest


@pytest.hookspec(firstresult=True)
def pytest_reporter_make_env(template_dirs, config):
    pass


def pytest_reporter_modify_env(env, config):
    pass


def pytest_reporter_context(config):
    pass


@pytest.hookspec(firstresult=True)
def pytest_reporter_render(env, template, context):
    pass


def pytest_reporter_finish(path, env, context, config):
    pass
