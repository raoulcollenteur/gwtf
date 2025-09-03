import numpy as np
import pandas as pd
import pytest

from gwtf.mcr import MCR


@pytest.fixture
def simple_wt():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    data = np.linspace(10, 20, 10)
    return pd.Series(data, index=idx)


def test_mcr_init():
    mcr = MCR()
    assert mcr.name == "MCR"
    assert mcr.nparam == 2


def test_get_fall_sections(simple_wt):
    mcr = MCR()
    falls = mcr.get_fall_sections(simple_wt)
    assert isinstance(falls, pd.DataFrame)


def test_get_dhdt(simple_wt):
    mcr = MCR()
    dhdt = mcr.get_dhdt(simple_wt)
    assert isinstance(dhdt, pd.Series)


def test_estimate_dhdt(simple_wt):
    mcr = MCR()
    # Set parameters for test
    mcr.parameters.loc[:, "optimal"] = [0.1, 0.2]
    dhdt_est = mcr.estimate_dhdt(simple_wt)
    assert isinstance(dhdt_est, pd.Series)


def test_fit_mcr_raises(simple_wt):
    mcr = MCR()
    # Test should raise an error
    with pytest.raises(Exception):
        mcr.fit_mcr(simple_wt)


def test_get_extrapolated(simple_wt):
    mcr = MCR()
    mcr.parameters.loc[:, "optimal"] = [0.1, 0.2]
    # Create dummy events
    idx = pd.date_range("2020-01-02", periods=5, freq="D")
    from pandas import IntervalIndex
    events = IntervalIndex.from_arrays(left=idx- pd.Timedelta(days=1), right=idx)
    result = mcr.get_extrapolated(simple_wt, events)
    assert isinstance(result, pd.Series)


def test_plot_runs(simple_wt):
    mcr = MCR()
    # Create a series with some variation for fitting
    idx = pd.date_range("2020-01-01", periods=20, freq="D")
    varied_data = np.sin(np.linspace(0, 2 * np.pi, 20)) + 15  # Sine wave around 15
    varied_wt = pd.Series(varied_data, index=idx)

    mcr.fit_mcr(varied_wt)
    ax = mcr.plot(varied_wt)
    assert ax is not None
