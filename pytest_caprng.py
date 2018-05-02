# -*- coding: utf-8 -*-

import pytest
import random


# =============================================================================


__version__ = "0.1.0"
RNG_STATES_K = 'caprng/rng_states'
NP_RNG_STATES_K = 'caprng/np_rng_states'


def pytest_addoption(parser):
    group = parser.getgroup('caprng')

    group.addoption('--caprng-global-stdlib',
                    action='store_true',
                    help="Cache random's state for replay on failure.")

    group.addoption('--caprng-global-np',
                    action='store_true',
                    help="Cache np.random's state for replay on failure.")


class CapRNGReportCapture:

    # =========================================================================
    # I'm still pawing my way through pytest. But, I ran into this thread:
    #
    #     https://github.com/pytest-dev/pytest/issues/230
    #
    # which inspired the current implementation. The gist is that
    # using this hook grants access to the success or failure of a test,
    # which allows me to serialize state to disk ONLY if the test failed.
    # =========================================================================

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        rep = outcome.get_result()
        setattr(item, "rep_" + rep.when, rep)


def pytest_configure(config):
    # =========================================================================
    # This loads plugins via classes as modules *only* when requested.
    # The serialization / deserialization of PRNGs isn't expensive for most
    # projects. But, it can be and unless your doing stochastic testing,
    # it's unnessessary.
    # =========================================================================
    requested_caches = []

    if config.getoption('--caprng-global-stdlib'):
        requested_caches.append(CapGlobalStdlibRNG)

    if config.getoption('--caprng-global-np'):
        requested_caches.append(CapGlobalNpRNG)

    if requested_caches:
        config.pluginmanager.register(CapRNGReportCapture())

        for cls in requested_caches:
            config.pluginmanager.register(cls())


def to_random_state(obj):
    """
    :param obj: the json deserialized representation of random.getstate()
    :return: an object suitable as an argument to random.setstate
    """
    return [tuple(el) if isinstance(el, list) else el for el in obj]


class CapGlobalStdlibRNG:

    @pytest.fixture(scope='session')
    def rng_state_cache(self, request):
        d = request.config.cache.get(RNG_STATES_K, {})
        yield d
        request.config.cache.set(RNG_STATES_K, d)

    @pytest.fixture(autouse=True)
    def capture_rng(self, request, rng_state_cache):
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


class CapGlobalNpRNG:

    def __init__(self):
        import numpy as np
        self.np = np

    @pytest.fixture(scope='session')
    def np_rng_state_cache(self, request):
        d = request.config.cache.get(NP_RNG_STATES_K, {})
        yield d
        request.config.cache.set(NP_RNG_STATES_K, d)

    @pytest.fixture(autouse=True)
    def capture_np_rng(self, request, np_rng_state_cache):
        k = request.node.nodeid

        last_state = np_rng_state_cache.get(k)
        if last_state is not None:
            self.np.random.set_state(last_state)
        else:
            state = self.np.random.get_state()
            np_rng_state_cache[k] = to_json_serializable_np_random_state(state)

        yield

        if not request.node.rep_call.failed:
            del np_rng_state_cache[k]
