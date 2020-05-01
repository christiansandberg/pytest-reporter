===============
pytest-reporter
===============

.. image:: https://img.shields.io/pypi/v/pytest-reporter.svg
    :target: https://pypi.org/project/pytest-reporter
    :alt: PyPI version

Generate `Pytest`_ reports from templates. You may use one of the available
templates on PyPI (like the reference template `html1`_), inherit them in your
own template to tweak their content and appearence or make your own from scratch.

Anything text based can be generated like HTML, LaTeX, CSV et.c.
The default engine is `Jinja2`_ but should be flexible enough to support many
other engines.


Installation
------------

You can install "pytest-reporter" via `pip`_ from `PyPI`_::

    $ pip install pytest-reporter


Usage
-----

Specify the template you want to use and the output path of the report::

    $ pytest --template=template/report.html --report=report.html


Writing templates
-----------------

TODO

See `html1`_ for a reference implementation.


Hooks
-----

TODO


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-reporter" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`html1`: https://pypi.org/project/pytest-reporter-html1
.. _`Jinja2`: https://jinja.palletsprojects.com/
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/christiansandberg/pytest-reporter/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
