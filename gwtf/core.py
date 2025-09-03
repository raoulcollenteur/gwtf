"""Main file with the methods to estimate the recharge.

Author: Raoul A. Collenteur, July 2025

"""

import pandas as pd


def validate_data(wt):
    """Internal method to validate the data.

    Parameters
    ----------
    wt : pd.Series
        Time series of the water table fluctuations.

    Raises
    ------
    ValueError
        If the data is not a Pandas Series or if the index is not a DatetimeIndex.

    """
    if not isinstance(wt, pd.Series):
        raise ValueError("The data should be a Pandas Series.")

    if not isinstance(wt.index, pd.DatetimeIndex):
        raise ValueError("The index of the data should be a DatetimeIndex.")

    if wt.empty:
        raise ValueError("The data is empty. Please provide a non-empty Pandas Series.")

