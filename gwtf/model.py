"""This file contains the Model class

Raoul Collenteur, 2025

"""

import matplotlib.pyplot as plt
from numpy import nan
from pandas import DataFrame, IntervalIndex, Series

from .core import validate_data


class Model:
    def __init__(self, wt, name=None, mcr=None):
        """Basic model to estimate groundwater recharge from water table data.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations. The index should be a
            DatetimeIndex.
        name : str, optional
            Name of the model, by default None
        mcr : MCR instance, optional
            Instance of the MCR class to use for extrapolation of the water table
            before computing the rises, by default None

        Notes
        -----
        The Model class can be used to estimate groundwater recharge from water table
        data. The recharge is estimated as the product of the rises in the water table
        and the specific yield (sy). The rises can be computed using different methods,
        which can be specified using the rise_rule parameter in the estimate method.

        If an instance of the MCR class is provided, the Master Recession Curve (MCR)
        is used to extrapolate the water table before computing the rises.

        """
        validate_data(wt)
        self.wt = wt.dropna()
        self.name = name

        # Settings dict
        self.settings = {
            "freq": "D",
            "use_mcr": None  # None means use MCR when available
        }

        self.parameters = DataFrame(index=["sy"], data=[[0.1, 0.1, 0.005]],
                                    columns=["initial", "optimal", "stderr"])

        self.filter = None
        self.mcr = mcr
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
            raise ValueError(
                "No MCR instance provided. Please provide an instance of "
                "the MCR class when creating the Model instance."
            )

        if tmin is None:
            tmin = self.wt.index.min()
        if tmax is None:
            tmax = self.wt.index.max()

        wt_fit = self.wt[(self.wt.index >= tmin) & (self.wt.index <= tmax)]

        self.mcr.fit_mcr(wt_fit)

    def get_recharge_event_intervals(self, wt: Series, rise_rule="rises") -> Series:
        """Method to get the intervals on which to compute the recharge.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        pd.IntervalIndex
            IntervalIndex with the events to compute the recharge on.

        """
        dt = wt.index.diff()[1:]
        dh = wt.diff()[1:]

        # Create an IntervalIndex for which the rises are computed
        dtint = IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

        changes = Series(index=dtint, data=dh.values)

        # 1. Get the points for which to consider the rises
        if rise_rule not in ["both", "rises"]:
            raise ValueError("rise_rule should be 'both' or 'rises'.")

        # Get only the rise sections
        if rise_rule == "rises":
            events_int = changes[changes.values > 0].index
        # Get every point
        elif rise_rule == "both":
            events_int = changes.index

        if events_int is None or events_int.empty:
            raise ValueError("No recharge events found. Please check the water table "
                             "data and the rise_method.")
        self.events = events_int
        return events_int

    def estimate_recharge(self, sy=None, fit_mcr=False, rise_rule="rises") -> Series:
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

        # 2. Get the points for which to consider the rises
        events_int = self.get_recharge_event_intervals(self.wt, rise_rule=rise_rule)

        # 3. Compute the rises
        if self.mcr is not None:
            # 3. Extrapolate using the MCR
            left_hand = self.mcr.get_extrapolated(self.wt, events_int)

        else:
            left_hand = Series(index=events_int.left, data=self.wt[events_int.left])

        #
        rises = Series(
            index=events_int,
            data=self.wt[events_int.right].values - left_hand.values,
        )

        rises = rises[rises.values > 0]
        self.rises = rises

        if sy is None:
            if self.parameters.loc["sy", "optimal"] is nan:
                raise ValueError("The specific yield is not set. Please provide a value "
                                 "for sy or set the optimal value using the "
                                 "self.parameters DataFrame.")
            else:
                sy = self.parameters.loc["sy", "optimal"]
        else:
            self.parameters.loc["sy", "optimal"] = sy

        # 3. Compute the recharge as the product of the events and the specific yield
        recharge = rises * sy

        # Set the index to the right side of the intervals
        recharge.index = rises.index.right
        recharge.name = "recharge"

        # Clip negative values to zero
        recharge[recharge < 0] = 0

        return recharge

    def plot(self, ax=None, figsize=(10, 6)):
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
            _, axs = plt.subplots(2, 1, sharex=True, figsize=figsize)

        # Plot the water table
        self.wt.plot(ax=axs[0], label="Water table", marker=".", ls="none", color="k")

        # Plot the rises
        if self.events is not None:
            for interval, rise in self.rises.items():
                axs[0].plot([interval.left, interval.right],
                            [self.wt.loc[interval.left],
                             self.wt.loc[interval.left] + rise],
                            lw=3, label="Rises", color="C1")

        # Plot the recharge
        if self.events is not None:
            self.estimate_recharge().plot(ax=axs[1], label="Recharge")

        axs[0].set_ylabel("Water table [m]")
        axs[0].legend(["Water table", "Rises"])

        axs[1].set_ylabel("Recharge [m/d]")
        axs[1].set_xlabel("Time")

        plt.tight_layout()

        return axs


