import pytest

from gwtf.core import validate_data


def test_validate_data_valid(valid_series):
    # Should not raise any error
    validate_data(valid_series)


def test_validate_data_not_series(not_a_series):
    with pytest.raises(ValueError, match="Pandas Series"):
        validate_data(not_a_series)


def test_validate_data_non_datetime_index(non_datetime_index_series):
    with pytest.raises(ValueError, match="DatetimeIndex"):
        validate_data(non_datetime_index_series)


def test_validate_data_empty(empty_series):
    with pytest.raises(ValueError, match="empty"):
        validate_data(empty_series)
