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
    if config.getoption("--template-engine") == "jinja2":
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


@pytest.hookimpl(trylast=True)
def pytest_reporter_render(env, template, context):
    if isinstance(env, Environment):
        return env.get_template(template).render(**context)
