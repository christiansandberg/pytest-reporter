import pytest
try:
    from mako.lookup import TemplateLookup
except ImportError:
    HAS_MAKO = False
else:
    HAS_MAKO = True


@pytest.hookimpl(trylast=True)
def pytest_reporter_make_env(template_dirs, config):
    if config.getoption("--template-engine") == "mako":
        if not HAS_MAKO:
            raise RuntimeError("Mako template engine not installed")
        return TemplateLookup(directories=template_dirs)


@pytest.hookimpl(trylast=True)
def pytest_reporter_render(env, template, context):
    if HAS_MAKO and isinstance(env, TemplateLookup):
        return env.get_template(template).render(**context)
