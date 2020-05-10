===============
pytest-reporter
===============

.. image:: https://img.shields.io/pypi/v/pytest-reporter.svg
    :target: https://pypi.org/project/pytest-reporter
    :alt: PyPI version

Generate `Pytest`_ reports from templates. You may use one of the available
templates on PyPI (like the reference template `pytest-reporter-html1`_),
inherit them in your own template to tweak their content and appearence or
make your own from scratch.

Anything text based can be generated like HTML, LaTeX, CSV et.c.


Installation
------------

You can install "pytest-reporter" via `pip`_ from `PyPI`_::

    $ pip install pytest-reporter


Usage
-----

Specify the template you want to use and the output path of the report::

    $ pytest --template-dir=templates --template=report.html --report=report.html


Writing templates
-----------------

This plugin does not come with built-in support for any template engines,
it is up to each template to implement the rendering (or use another template
plugin as base). A minimal template may just implement the
``pytest_reporter_render`` hook.

This is a very basic Jinja2 template implementation:

.. code:: python

    from jinja2 import Environment, FileSystemLoader, TemplateNotFound

    def pytest_reporter_render(template_name, dirs, context):
        env = Environment(loader=FileSystemLoader(dirs))
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            return
        return template.render(context)

See `pytest-reporter-html1`_ for a full reference implementation.


The template context
--------------------

The standard context available for all templates include the following:

* ``config``: `Config <https://docs.pytest.org/en/latest/reference.html#_pytest.config.Config>`_
* ``session``: `Session <https://docs.pytest.org/en/latest/reference.html#_pytest.main.Session>`_
* ``started``: Unix timestamp
* ``ended``: Unix timestamp
* ``warnings``: List of warnings.WarningMessage
* ``tests``: List of dictionaries with the following keys:

  * ``item``: `Item <https://docs.pytest.org/en/latest/reference.html#_pytest.nodes.Item>`_
  * ``phases``: List of dictionaries with the following keys:

    * ``call``: `CallInfo <https://docs.pytest.org/en/latest/reference.html#_pytest.runner.CallInfo>`_
    * ``report``: `TestReport <https://docs.pytest.org/en/latest/reference.html#_pytest.runner.TestReport>`_
    * ``log_records``: List of `logging.LogRecord <https://docs.python.org/3/library/logging.html#logging.LogRecord>`_
    * ``status``: Dictionary with the following keys:

      * ``category``: Category of the status or empty string
      * ``letter``: Single letter version of status or empty string
      * ``word``: Uppercase word version of status or empty string
      * ``style``: Dictionary with ``{"color": True}`` or empty dictionary

  * ``status``: Dictionary with the following keys:

    * ``category``: Category of the test status
    * ``letter``: Single letter version of test status
    * ``word``: Uppercase word version of test status
    * ``style``: Dictionary with ``{"color": True}`` or empty dictionary

The context may be extended or modified using the following methods:

* ``config.template_context``
* The ``template_context`` fixture
* The ``function_context`` fixture (for the current ``tests`` item)
* The ``pytest_reporter_context()``  hook


Hooks
-----

See `hooks.py`_ for a complete list of hooks available.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-reporter" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`pytest-reporter-html1`: https://pypi.org/project/pytest-reporter-html1
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/christiansandberg/pytest-reporter/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
.. _`hooks.py`: https://github.com/christiansandberg/pytest-reporter/blob/develop/pytest_reporter/hooks.py
