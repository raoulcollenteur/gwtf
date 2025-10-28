import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def valid_series():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    return pd.Series(np.random.rand(10), index=idx)


@pytest.fixture
def empty_series():
    idx = pd.date_range("2020-01-01", periods=0, freq="D")
    return pd.Series([], index=idx)


@pytest.fixture
def non_datetime_index_series():
    return pd.Series([1, 2, 3], index=[0, 1, 2])


@pytest.fixture
def not_a_series():
    return [1, 2, 3]
