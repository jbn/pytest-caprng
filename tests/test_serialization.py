import json
import random
import numpy as np
import pytest_caprng


def test_random_state_serialization():
    orig_state = random.getstate()
    json_transduced = json.loads(json.dumps(orig_state))
    bak_state = pytest_caprng.to_random_state(json_transduced)

    random.random()  # Mutate the state.
    assert orig_state != random.getstate()

    random.setstate(bak_state)
    assert orig_state == random.getstate()


def test_np_random_state_serialization():
    orig_state = np.random.get_state()
    bak_state = pytest_caprng.to_json_serializable_np_random_state(orig_state)

    # =========================================================================
    # mutate the state and take a sample. mt has a very long period. the
    # probability of two equal floating point samples is very, very low.
    # since i'm not sure if the state structure will change and testing for
    # array equality requires array comparisons not the == operator, this
    # is a cleaner test.
    # =========================================================================
    orig_sample = np.random.random()

    np.random.set_state(bak_state)
    restored_sample = np.random.random()

    assert orig_sample == restored_sample
