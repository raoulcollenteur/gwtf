"""Main file with the methods to estimate the recharge.

Author: Raoul A. Collenteur, July 2025

"""

import pandas as pd


def estimate_recharge(events, sy=0.2, sy_uncertainty=0.05):
    # if a single number, assume it is a percentage
    if isinstance(sy_uncertainty, float):
        sy_lower = sy - sy_uncertainty * sy
        sy_upper = sy + sy_uncertainty * sy

    r = []

    for s in [sy, sy_lower, sy_upper]:
        r.append(s * events)  # / dt)

    r = pd.concat(r, axis=1, names=["mean", "lower", "upper"])

    return r


def extract_events(wt: pd.Series, method: str = "Rise") -> pd.DataFrame:
    """Method to extract individual recharge events.

    Parameters
    ----------
    wt : pd.Series
        Time series of the water table fluctations.
    method : str, optional
       The method to use to determine the individual events, by default "Rise". Options
       are "RISE" and "MCR" for now.

    Returns
    -------
    pd.DataFrame
        _description_
    """
    # Check the data before doing any computations
    _validate_data(wt)

    # Extract the individual events

    if method == "RISE":
        rises = rise_method(wt)
    # elif method == "MCR":
    #     rises = mcr_method(wt)
    else:
        raise KeyError(f"The method {method} is not available.")

    return rises

def rise_method(wt) -> pd.DataFrame:
    """Using the RISE method to compute the recharge events.

    Parameters
    ----------
    wt: pd.Series
        time series of the water table fluctuations.

    Return
    ------
    rises: pd.DataFrame
        DataFrame with a IntervalIndex and the rises.

    Notes
    -----
    Simplest method to select the rises over time.

    """
    dt = wt.index.diff()[1:]  # / pd.Timedelta("1D")
    dh = wt.diff()[1:]

    dtint = pd.IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

    rises = pd.DataFrame(index=dtint, data=dh.values)
    rises = rises[rises.values > 0]
    return rises

def _validate_data(wt):
    return