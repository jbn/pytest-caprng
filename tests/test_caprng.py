# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest('--help')

    result.stdout.fnmatch_lines([
        'caprng:',
        "*--capture-rng*Cache random's state*",
        "*--capture-np-rng*Cache np.random's state*",
    ])


# def test_bar_fixture(testdir):
#     """Make sure that pytest accepts our fixture."""

#     # create a temporary pytest test module
#     testdir.makepyfile("""
#         def test_random_good():
#             import random
#             assert random.random() <= 1.0
#     """)

#     result = testdir.runpytest('--capture-rng')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_random_good PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0


# def test_bar_fixture(testdir):
#     """Make sure that pytest accepts our fixture."""

#     # create a temporary pytest test module
#     testdir.makepyfile("""
#         import random

#         def test_sth(bar):
#             assert random.random() == 0.5
#     """)

#     result = testdir.runpytest('--capture-rng')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_sth PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0


# def test_hello_ini_setting(testdir):
#     testdir.makeini("""
#         [pytest]
#         HELLO = world
#     """)

#     testdir.makepyfile("""
#         import pytest

#         @pytest.fixture
#         def hello(request):
#             return request.config.getini('HELLO')

#         def test_hello_world(hello):
#             assert hello == 'world'
#     """)

#     result = testdir.runpytest('-v')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_hello_world PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
