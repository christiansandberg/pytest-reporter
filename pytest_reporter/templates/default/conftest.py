from datetime import datetime

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_reporter_modify_env(env):
    env.add_extension("jinja2.ext.debug")
    env.filters["strftime"] = lambda ts, fmt: datetime.fromtimestamp(ts).strftime(fmt)
