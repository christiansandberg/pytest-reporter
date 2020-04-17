import datetime


def pytest_reporter_modify_env(env):
    env.add_extension("jinja2.ext.debug")
    env.filters["datetime"] = datetime.datetime.fromtimestamp
    env.filters["strftime"] = datetime.datetime.strftime
