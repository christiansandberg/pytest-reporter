import pytest
try:
    from jinja2 import (
        Environment,
        FileSystemLoader,
        select_autoescape,
    )
except ImportError:
    HAS_JINJA2 = False
else:
    HAS_JINJA2 = True


@pytest.hookimpl(trylast=True)
def pytest_reporter_make_env(template_dirs, config):
    if config.getoption("--template-engine") == "jinja2":
        if not HAS_JINJA2:
            raise RuntimeError("Jinja2 template engine not installed")
        return Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(["html", "htm", "xml"]),
            # trim_blocks=True,
            # lstrip_blocks=True,
        )


@pytest.hookimpl(trylast=True)
def pytest_reporter_render(env, template, context):
    if HAS_JINJA2 and isinstance(env, Environment):
        return env.get_template(template).render(**context)
