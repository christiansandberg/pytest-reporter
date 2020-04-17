import pytest


@pytest.hookspec(firstresult=True)
def pytest_reporter_make_env(template_dirs, config):
    pass


def pytest_reporter_modify_env(env, config):
    pass


@pytest.hookspec(firstresult=True)
def pytest_reporter_template(env, name, config):
    pass


def pytest_reporter_context(config):
    pass


@pytest.hookspec(firstresult=True)
def pytest_reporter_render(template, context):
    pass


@pytest.hookspec(firstresult=True)
def pytest_reporter_save(content, path, env, config):
    pass
