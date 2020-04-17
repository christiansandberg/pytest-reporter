from pathlib import Path

import pytest
from jinja2 import (
    Environment,
    ChoiceLoader,
    FileSystemLoader,
    PackageLoader,
    select_autoescape,
)


@pytest.hookimpl(trylast=True)
def pytest_reporter_make_env(template_dirs, config):
    return Environment(
        loader=ChoiceLoader(
            [
                FileSystemLoader(template_dirs),
                PackageLoader("pytest_reporter", "templates"),
            ]
        ),
        autoescape=select_autoescape(["html", "htm", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def pytest_reporter_modify_env(env, config):
    pass


@pytest.hookimpl(trylast=True)
def pytest_reporter_template(env, name, config):
    return env.get_template(name)


def pytest_reporter_context(config):
    return getattr(config, "template_context", {})


@pytest.hookimpl(trylast=True)
def pytest_reporter_render(template, context):
    return template.render(**context)


def pytest_reporter_save(content, path, env, config):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
