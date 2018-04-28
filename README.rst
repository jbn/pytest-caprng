=============
pytest-caprng
=============

.. image:: https://img.shields.io/pypi/v/pytest-caprng.svg
    :target: https://pypi.org/project/pytest-caprng
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-caprng.svg
    :target: https://pypi.org/project/pytest-caprng
    :alt: Python versions

.. image:: https://travis-ci.org/jbn/pytest-caprng.svg?branch=master
    :target: https://travis-ci.org/jbn/pytest-caprng
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/jbn/pytest-caprng?branch=master
    :target: https://ci.appveyor.com/project/jbn/pytest-caprng/branch/master
    :alt: See Build Status on AppVeyor


A plugin that replays pRNG state on failure.

----

Why is this?
-------------

Testing stochastic functions is challenging. Crudely, one of two things happens:

1. *You learn to ignore sporadic failures.* For example, if you constructed a `binomial_test <https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.binom_test.html>`_ over some stochastic function, there is some probability it will fail. Knowing this, you rerun the test; it works; you conclude there is no problem. Usually, that is the correct conclusion. But, repeating this pattern over and over will blind you to genuinely faulty code. This makes bug discovery less likely. This is bad.

2. *You monkey patch your pRNG.* Usually, this means scheduling realizations, injecting determinism. But, this requires knowing the implementation details of the function your testing. And, if that changes, the test needs a change, too. This is fragile. This makes bug discovery less likely. This is bad.

This plugin is a compromise meant to eliminate (2) and reduce the prevalence of (1). It lends *some* degree of determinism to your tests by means of reproducibility. **If your stochastic test fails, rerunning it will result in the exact same failure**. 

How it works?
----------------

Unless you have (cool) specialized hardware, your code doesn't use random numbers. Instead, it uses a deterministic sequences of numbers produced by a Pseudo Random Number Generator (PRNG) that is "random enough." Each PRNG has an internal state. When you draw a sample, the state changes. If you reset the PRNG's state back to the original state, then sample again, the sample will be identical to the first one. It's deterministic.

This plugin exploits that determinism for the PRNGs underlying ``random`` and ``np.random``. Prior to each test function, caprng [cap]tures the p[rng] state. If the test fails, the plugin writes the captured state to the cache. Then, when you rerun the tests, the plugin looks to see if your test function has any associated, cached PRNG state. If it does, it overwrites PRNG state to *prior* to running the test function, **exactly reproducing the failing tests prior environment**.


Installation
------------

You can install "pytest-caprng" via::

    $ pip install pytest-caprng


Usage
-----

For ``random``-based state capturing::

    $ pytest --capture-rng

And for ``np.random``::

    $ pytest --capture-np-rng

You probably should add the option to your pytest.ini file::

    [pytest]
    addopts = --capture-rng --capture-np-rng

so that you don't "miss" reproducible errors.

Contributing
------------
Contributions are very welcome. Tests can be run with ``tox``, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the MIT license, "pytest-caprng" is free and open source software


Issues
------

If you encounter any problems, please file an issue along with a detailed description.
