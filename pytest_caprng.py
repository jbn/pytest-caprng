# -*- coding: utf-8 -*-

import pytest
import random
import numpy as np


def pytest_addoption(parser):
    group = parser.getgroup('caprng')

    group.addoption('--capture-rng',
                    action='store_true',
                    help="Cache random's state for replay on failure.")

    group.addoption('--capture-np-rng',
                    action='store_true',
                    help="Cache np.random's state for replay on failure.")

# =============================================================================


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# =============================================================================
# random based.
# =============================================================================


def to_random_state(obj):
    """
    :param obj: the json deserialized representation of random.getstate()
    :return: an object suitable as an argument to random.setstate
    """
    return [tuple(el) if isinstance(el, list) else el for el in obj]


@pytest.fixture(scope='session')
def rng_state_cache(request):
    k = 'caprng/prng_states'

    d = request.config.cache.get(k, {})
    yield d
    request.config.cache.set(k, d)


@pytest.fixture(autouse=True)
def capture_rng(request, rng_state_cache):
    # if request.config.getoption('capture-rng'):
    k = request.node.nodeid

    last_state = rng_state_cache.get(k)
    if last_state is not None:
        random.setstate(to_random_state(last_state))
    else:
        rng_state_cache[k] = random.getstate()

    yield

    if not request.node.rep_call.failed:
        del rng_state_cache[k]


# =============================================================================
# numpy.random based.
# =============================================================================


def to_json_serializable_np_random_state(state):
    """
    :param state: the np.random.get_state()
    :return: a json serializable representation of the state.
    """
    # I think it's always MT19937-based but I may be wrong and it may change.
    return [el.tolist() if hasattr(el, 'tolist') else el for el in state]


@pytest.fixture(scope='session')
def np_rng_state_cache(request):
    # if request.config.getoption('random_replay'):
    k = 'caprng/np_prng_states'
    d = request.config.cache.get(k, {})
    yield d
    request.config.cache.set(k, d)


@pytest.fixture(autouse=True)
def capture_np_rng(request, np_rng_state_cache):
    k = request.node.nodeid

    last_state = np_rng_state_cache.get(k)
    if last_state is not None:
        np.random.set_state(last_state)
    else:
        state = np.random.get_state()
        np_rng_state_cache[k] = to_json_serializable_np_random_state(state)

    yield

    if not request.node.rep_call.failed:
        del np_rng_state_cache[k]
