"""Main file with the methods to estimate the recharge.

Author: Raoul A. Collenteur, July 2025

"""

import pandas as pd


def estimate_recharge(events, sy=0.2, sy_uncertainty=0.05, freq="D") -> pd.DataFrame:
    """Method to estimate the recharge from the water table fluctuations.

    Parameters
    ----------
    events : _type_
        Pandas DataFrame with the individual recharge events. The index should be an
        IntervalIndex with the start and end of the event. The values should be the
        water table rises during the event.
    sy : float, optional
        Estimate of the specific yield to use in the water table fluctuations method,
        by default 0.2.
    sy_uncertainty : float, optional
        Estimate of the uncertainty in the specific yield. If a single number is
        provided it is interpreted as a percentage. If a list of two number is provided
        these are interpreted as the lower and upper bound of the estimate. by default
        0.05.
    freq : str, optional
        The frequency to use for the resampling of the recharge, by default "D" for
        daily. Options are D, H, min, s, ms, us, ns. For irregular frequencies, such as
        month ("M") or year ("Y"), resample the results to the desired frequency after
        the recharge has been estimated.

    Returns
    -------
    pd.DataFrame:
        _description_
    """
    # Check the data before doing any computations
    if not isinstance(events, pd.DataFrame):
        raise ValueError("The events should be a Pandas DataFrame.")
    if not isinstance(events.index, pd.IntervalIndex):
        raise ValueError("The index of the events should be an IntervalIndex.")
    if events.empty:
        raise ValueError(
            "The events are empty. Please provide a non-empty Pandas DataFrame."
        )
    if not isinstance(events.index.left, pd.DatetimeIndex):
        raise ValueError("The left side of the intervals should be a DatetimeIndex.")
    if not isinstance(events.index.right, pd.DatetimeIndex):
        raise ValueError("The right side of the intervals should be a DatetimeIndex.")
    if not isinstance(sy, (float, int)):
        raise ValueError("The specific yield (sy) should be a float or an int.")
    if sy < 0 or sy > 1:
        raise ValueError("The specific yield (sy) should be between 0 and 1.")
    if not isinstance(sy_uncertainty, (float, list)):
        raise ValueError(
            "The specific yield uncertainty (sy_uncertainty) should be a float or a list."
        )
    if isinstance(sy_uncertainty, float) and (sy_uncertainty < 0 or sy_uncertainty > 1):
        raise ValueError(
            "If sy_uncertainty is a float, it should be between 0 and 1 (percentage)."
        )
    if isinstance(sy_uncertainty, list) and len(sy_uncertainty) != 2:
        raise ValueError(
            "If sy_uncertainty is a list, it should contain two floats (lower and upper "
            "bound of the uncertainty)."
        )
    if not isinstance(freq, str):
        raise ValueError("The frequency (freq) should be a string.")
    if freq not in ["D", "H", "min", "s", "ms", "us", "ns"]:
        raise ValueError(
            "The frequency (freq) should be one of the following: 'D', 'H', 'min', 's', "
            "'ms', 'us', 'ns'. For irregular frequencies, such as month ('M') or year "
            "('Y'), resample the results to the desired frequency after the recharge has "
            "been estimated."
        )

    # if a single number, assume it is a percentage
    if isinstance(sy_uncertainty, float):
        sy_lower = sy - sy_uncertainty * sy
        sy_upper = sy + sy_uncertainty * sy
    # if a list of two numbers, assume they are the lower and upper bound
    elif isinstance(sy_uncertainty, list) and len(sy_uncertainty) == 2:
        sy_lower = sy_uncertainty[0]
        sy_upper = sy_uncertainty[1]
    else:
        raise ValueError(
            "sy_uncertainty should be a float or a list of two floats "
            "(lower and upper bound of the uncertainty)."
        )

    r = []

    # Calculate the recharge for each event
    for s in [sy, sy_lower, sy_upper]:
        r.append(s * events)

    # Create a DataFrame with the recharge estimates
    r = pd.concat(r, axis=1, names=["mean", "lower", "upper"])

    # Compute the time intervals for the events
    dt = (events.index.right - events.index.left) / pd.Timedelta(f"1{freq}")

    # Set the index to the right side of the intervals
    r.index = events.index.right

    # Resample the recharge to the desired frequency and fill missing values
    # by backfilling
    recharge = r.divide(dt, axis=0).resample(f"{freq}").bfill()

    return recharge


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
        DataFrame with a IntervalIndex and the rises. The index is an IntervalIndex
        with the start and end of the rise, and the values are the water table rises
        during the rise.

    Notes
    -----
    Simplest method to select the rises over time. It computes the difference between
    the water table levels and the time intervals between the measurements. The
    resulting DataFrame has an IntervalIndex with the start and end of the rise, and
    the values are the water table rises for each interval.

    """
    dt = wt.index.diff()[1:]
    dh = wt.diff()[1:]

    # Create an IntervalIndex for which the rises are computed
    dtint = pd.IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

    rises = pd.DataFrame(index=dtint, data=dh.values)

    # Only keep the rises that are positive
    rises = rises[rises.values > 0]
    return rises


def mcr_method(wt) -> pd.DataFrame:
    """Using the MCR method to compute the recharge events.

    Parameters
    ----------
    wt: pd.Series
        time series of the water table fluctuations.

    Return
    ------
    rises: pd.DataFrame
        DataFrame with a IntervalIndex and the rises. The index is an IntervalIndex
        with the start and end of the rise, and the values are the water table rises
        during the rise.

    Notes
    -----
    This method is not implemented yet.
    """
    raise NotImplementedError("The MCR method is not implemented yet.")


def _validate_data(wt):
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
