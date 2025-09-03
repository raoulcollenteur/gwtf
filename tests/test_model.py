import numpy as np
import pandas as pd
import pytest

from gwtf.model import Model


@pytest.fixture
def simple_wt():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    data = np.linspace(10, 20, 10)
    return pd.Series(data, index=idx)


def test_model_init_valid(simple_wt):
    m = Model(simple_wt)
    assert isinstance(m.wt, pd.Series)
    assert m.wt.index.is_monotonic_increasing


def test_model_init_invalid():
    with pytest.raises(ValueError):
        Model([1, 2, 3])


def test_get_recharge_event_intervals(simple_wt):
    m = Model(simple_wt)
    events = m.get_recharge_event_intervals(m.wt)
    assert hasattr(events, "left")
    assert hasattr(events, "right")


def test_estimate_recharge(simple_wt):
    m = Model(simple_wt)
    recharge = m.estimate_recharge(sy=0.1)
    assert isinstance(recharge, pd.Series)
    assert (recharge >= 0).all()


def test_estimate_recharge_no_rises():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    data = np.linspace(20, 10, 10)  # strictly decreasing
    wt = pd.Series(data, index=idx)
    m = Model(wt)
    with pytest.raises(ValueError):
        m.get_recharge_event_intervals(m.wt)


def test_plot_runs(simple_wt):
    m = Model(simple_wt)
    m.estimate_recharge(sy=0.1)
    axs = m.plot()
    assert axs is not None
