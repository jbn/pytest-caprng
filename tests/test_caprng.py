# -*- coding: utf-8 -*-
import re


RANDOM_ERROR_RE = re.compile(r"^E\s+assert 0\.\d+\s+==\s+-1.0", re.M)
NP_RANDOM_ERROR_RE = re.compile(r"^E\s+AssertionError:\s+"
                                "assert 0\.\d+\s+==\s+-1.0", re.M)


def test_help_message(testdir):
    result = testdir.runpytest('--help')

    result.stdout.fnmatch_lines([
        'caprng:',
        "*--capture-rng*Cache random's state*",
        "*--capture-np-rng*Cache np.random's state*",
    ])


def test_random_reproducibility(testdir):

    testdir.makepyfile("""
        import random

        def test_random_works():
            assert random.random() == -1.0
    """)

    result = testdir.runpytest('--capture-rng')
    assert result.ret == 1, "It should fail the first time."
    first_error = RANDOM_ERROR_RE.search(result.stdout.str()).group(0)

    assert result.ret == 1, "It should fail the second time."
    second_error = RANDOM_ERROR_RE.search(result.stdout.str()).group(0)

    assert first_error == second_error, "But the errors should exactly match."


def test_np_random_reproducibility(testdir):

    testdir.makepyfile("""
        import numpy as np

        def test_np_random_works():
            assert np.random.random() == -1.0
    """)

    result = testdir.runpytest('--capture-np-rng')
    assert result.ret == 1, "It should fail the first time."
    first_error = NP_RANDOM_ERROR_RE.search(result.stdout.str()).group(0)

    assert result.ret == 1, "It should fail the second time."
    second_error = NP_RANDOM_ERROR_RE.search(result.stdout.str()).group(0)

    assert first_error == second_error, "But the errors should exactly match."
