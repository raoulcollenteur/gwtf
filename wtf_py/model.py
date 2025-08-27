"""This file contains the Model class

Raoul Collenteur, 2025

"""

import matplotlib.pyplot as plt
from numpy import nan
from pandas import DataFrame, Timedelta

from .core import validate_data
from .rises import RISE


class Model:
    def __init__(self, wt, name=None, rise_method=RISE()):
        """Basic model to estimate groundwater recharge from water table data.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations. The index should be a
            DatetimeIndex.
        name : str, optional
            Name of the model, by default None
        rise_method : rise instance, optional
            Method to extract the rises from the water table data, by default RISE()
        """
        validate_data(wt)
        self.wt = wt
        self.name = name

        # Settings dict
        self.settings = {
            "freq": "D",
            "use_mcr": None  # None means use MCR when available
        }

        self.parameters = DataFrame(index=["sy"], data=[[0.1, 0.1, 0.005]],
                                    columns=["initial", "optimal", "stderr"])

        self.filter = None
        self.rise_method = rise_method
        self.events = None

    def fit_mcr(self, tmin=None, tmax=None):
        """Method to fit the Master Recession Curve (MCR).

        Parameters
        -----------
        tmin: pd.Timestamp
            Start of the period to use for the fitting. If None, the start of the time
            series is used.
        tmax: pd.Timestamp
            End of the period to use for the fitting. If None, the end of the time
            series is used.

        Notes
        -----


        """
        if self.mcr is None:
            pass

    def get_events(self, rise_rule="rises", **kwargs):
        """Method to get the recharge events from the water table data.

        Parameters
        ----------
        **kwargs: keyword arguments
            Additional keyword arguments to pass to the rise_method.get_rises method.

        Returns
        -------
        pd.DataFrame
            DataFrame with the recharge events. The index is an IntervalIndex with the
            start and end of the rise, and the values are the water table rises for each
            interval.

        """
        self.events = self.rise_method.get_rises(self.wt, rise_rule=rise_rule, **kwargs)

        if self.events is None or self.events.empty:
            raise ValueError("No recharge events found. Please check the water table "
                             "data and the rise_method.")

        return self.events


    def estimate(self, sy=None, fit_mcr=False, rise_rule="rises") -> DataFrame:
        """Method to estimate the groundwater recharge.

        Parameters
        ----------
        use_mcr: bool
            Set True to use the Master Recession Curve to extrapolate the watertable
            before computing the rises. Set False to not extrapolate. Defaults to None,
            which means that the MCR is used when present.

        Returns
        -------
        pandas.Series:
            Pandas Series with a DatetimeIndex and the values of the recharge estimates.


        Notes
        -----
        The recharge is estimated as the product of the rises and the specific yield.
        The recharge is resampled to the frequency defined in self.settings['freq'].
        Missing values are filled by backfilling.

        The following steps are performed:
        1. If fit_mcr is True, the MCR is fitted to the water table data.
        2. The rises are extracted from the water table data using the rise_method.
        3. The recharge is computed as the product of the rises and the specific yield.
        4. The recharge is resampled to the frequency defined in self.settings['freq'].
           Missing values are filled by backfilling.

        """
        # 1. Fit the MCR if requested
        if fit_mcr:
            self.fit_mcr()

        # 2. Get the recharge events
        events = self.get_events(rise_rule=rise_rule)

        if sy is None:
            if self.parameters.loc["sy", "optimal"] is nan:
                raise ValueError("The specific yield is not set. Please provide a value "
                                 "for sy or set the optimal value using the "
                                 "self.parameters DataFrame.")
            else:
                sy = self.parameters.loc["sy", "optimal"]

        freq = self.settings["freq"]

        # 3. Compute the recharge as the product of the events and the specific yield
        recharge = events * sy

        # Compute the time intervals for the events
        dt = (events.index.right - events.index.left) / Timedelta(f"1{freq}")

        # Set the index to the right side of the intervals
        recharge.index = events.index.right

        # Resample the recharge to the desired frequency and fill missing values
        # by backfilling
        recharge = recharge.divide(dt, axis=0).resample(f"{freq}").bfill()

        # CLip negative values to zero
        recharge[recharge < 0] = 0

        return recharge

    def plot(self, ax=None):
        """Method to plot the water table, the rises and the recharge.

        Parameters
        ----------
        ax: matplotlib.axes.Axes or None
            Axes to plot the water table, rises and recharge on. If None, a new
            figure and axes are created.

        Returns
        -------
        ax: matplotlib.axes.Axes
            Axes with the water table, rises and recharge.


        """
        if ax is None:
            _, axs = plt.subplots(2,1, sharex=True, figsize=(10,6))

        # Plot the water table
        self.wt.plot(ax=axs[0], label="Water table", marker=".", ls="none", color="k")

        # Plot the rises
        if self.events is not None:
            for interval, rise in self.events.itertuples():
                axs[0].plot([interval.left, interval.right],
                            [self.wt.loc[interval.left],
                             self.wt.loc[interval.left] + rise],
                            lw=3, label="Rises", color="C1")

        # Plot the recharge
        if self.events is not None:
            self.estimate().plot(ax=axs[1], label="Recharge")

        axs[0].set_ylabel("Water table [m]")
        axs[1].set_ylabel("Recharge [m/d]")
        axs[1].set_xlabel("Time")

        plt.tight_layout()

        return axs


