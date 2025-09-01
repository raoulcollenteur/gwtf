"""The file contains the methods to estimate the Master Recession Curve (MCR).

Raoul Collenteur, 2025
"""

import matplotlib.pyplot as plt
from pandas import DataFrame, IntervalIndex, Series
from scipy.optimize import curve_fit


class MCR:
    def __init__(self):
        """__init__ _summary_"""
        self.name = "MCR"
        self.nparam = 2
        self.parameters = DataFrame(
            index=["a", "b"],
            data=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            columns=["initial", "optimal", "stderr"],
        )

    def get_rises(self, wt, rise_rule="rises") -> DataFrame:
        """Method to get the rises from the water table data.

        Parameters
        ----------
        wt: pd.Series
            time series of the water table fluctuations.
        rise_rule: str, optional
            Rule to define the rises. Options are 'both' or 'rises'. 'both' means that
            both the rises and the extrapolated values using the MCR are used to define
            the rises. 'rises' means that only the rises are used to define the rises.
            Default is 'both'.

        Return
        ------
        rises: pd.DataFrame
            DataFrame with a IntervalIndex and the rises. The index is an IntervalIndex
            with the start and end of the rise, and the values are the water table rises
            during the rise.

        """
        # 1. Get the points for which to consider the rises
        events_int = self.get_recharge_sections(wt, rise_rule=rise_rule)

        # 2. Extrapolate using the MCR
        extrapolated = self.get_extrapolated(wt, events_int)

        # 3. Compute the rises
        rises = DataFrame(
            index=events_int, data=wt[events_int.right].values - extrapolated.values
        )

        # 4. Return the rises
        return rises[rises.values > 0]

    def get_fall_sections(self, wt: Series) -> DataFrame:
        """Internal method to get the fall sections of the water table fluctuations.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        pd.DataFrame
            DataFrame with the fall sections of the water table fluctuations.
        """
        dt = wt.index.diff()[1:]
        dh = wt.diff()[1:]

        # Create an IntervalIndex for which the rises are computed
        dtint = IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

        changes = DataFrame(index=dtint, data=dh.values)

        # Only keep the falls that are negative
        falls = changes[changes.values < 0]

        return DataFrame(index=dtint, data=falls.values)

    def get_dhdt(self, wt: Series) -> Series:
        """Internal method to get the dh/dt values of the water table fluctuations.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        pd.Series
            Series with the dh/dt values of the water table fluctuations.
        """
        dt = wt.index.diff()[1:].total_seconds() / (3600 * 24)

        dh = wt.diff()[1:]
        dhdt = dh / dt
        dhdt.index = dh.index

        return dhdt[dhdt < 0]

    def estimate_dhdt(self, wt, a=None, b=None):
        """estimate_dhdt from parameters and the water table

        Parameters
        ----------
        wt :

        """
        if a is None or b is None:
            a, b = self.parameters.optimal.values

        dhdt_est = -a * wt + b
        return dhdt_est

    def fit_mcr(self, wt: Series):
        """Method to fit the Master Recession Curve (MCR) to the water table data.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        None

        Notes
        -----
        This method is not implemented yet.
        """
        # Fit the MCR to the water table data using curve_fit
        dhdt = self.get_dhdt(wt)
        popt, pcov = curve_fit(
            f=self.estimate_dhdt, xdata=wt.loc[dhdt.index], ydata=dhdt
        )

        self.parameters.optimal = popt
        self.parameters.stderr = pcov.diagonal() ** 0.5

    def get_extrapolated(self, wt: Series, events: IntervalIndex, p=None) -> Series:
        """Internal method to get the extrapolated values using the MCR.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.
        events : pd.IntervalIndex
            IntervalIndex with the rise sections of the water table fluctuations.

        Returns
        -------
        pd.Series
            Series with the extrapolated values using the MCR.

        Notes
        -----
        This method is not implemented yet.
        """
        if p is None:
            a, b = self.parameters.optimal.values

        recession = self.estimate_dhdt(wt[events.left], a, b)
        return wt[events.left] + recession.values

    def plot():
        """Plot the fittedmaster recession curve for diagnostic checking."""
        _, ax = plt.subplots(figsize=(6, 4))

        # plt.plot(wt.loc[dhdt.index], -dhdt, marker=".", linestyle=" ", color="k")
        # plt.plot(wt.loc[dhdt.index], -dhdt_est, color="C1")

        ax.set_xlabel("Water table (m asl)")
        ax.set_ylabel("-dh/dt (m/d)")

        return ax
