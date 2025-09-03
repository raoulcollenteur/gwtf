"""The file contains the methods to estimate the Master Recession Curve (MCR).

Raoul Collenteur, 2025
"""

import matplotlib.pyplot as plt
from pandas import DataFrame, IntervalIndex, Series
from scipy.optimize import curve_fit


class MCR:
    def __init__(self):
        """Master Recession Curve (MCR) class to fit and apply the MCR.

        Notes
        -----
        The MCR is a simple linear recession model that can be used to estimate the
        recession of the water table. The MCR is defined as:

            dh/dt = -a * h + b

        where h is the water table, a and b are the parameters of the MCR.

        The MCR can be fitted to the falling sections of the water table fluctuations.
        The falling sections are defined as the sections where the water table is
        decreasing. The MCR can be used to extrapolate the water table during rise
        events.

        """
        self.name = "MCR"
        self.nparam = 2
        self.parameters = DataFrame(
            index=["a", "b"],
            data=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            columns=["initial", "optimal", "stderr"],
        )
        self.fall_sections = None
        self.dhdt = None

    def get_fall_sections(self, wt: Series) -> DataFrame:
        """Get the fall sections of the water table fluctuations.

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
        fall_sections = changes[changes.values < 0]

        return fall_sections

    def get_dhdt(self, wt: Series) -> Series:
        """Get the dh/dt values from the water table fluctuations.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        pd.Series
            Series with the dh/dt values of the water table fluctuations.

        Notes
        -----
        The dh/dt values are only computed for the falling sections of the water table
        fluctuations.

        """
        # Compute the time differences in days
        dt = wt.index.diff()[1:].total_seconds() / (3600 * 24)

        # Compute the differences in water table
        dh = wt.diff()[1:]

        # Compute dh/dt
        dhdt = dh / dt
        dhdt.index = dh.index

        return dhdt[dhdt < 0]

    def estimate_dhdt(self, wt, a=None, b=None):
        """estimate_dhdt from parameters and the water table

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.
        a : float, optional
            Parameter a of the MCR, by default None
        b : float, optional
            Parameter b of the MCR, by default None

        Returns
        -------
        pd.Series
            Series with the estimated dh/dt values of the water table fluctuations.

        Notes
        -----
        If a and b are not provided, the optimal parameters from the fit are used.

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
        self.dhdt = dhdt
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

    def plot(self, wt) -> plt.Axes:
        """Plot the fittedmaster recession curve for diagnostic checking."""
        _, ax = plt.subplots(figsize=(6, 4))

        dhdt_est = self.estimate_dhdt(wt.loc[self.dhdt.index])

        plt.plot(
            wt.loc[self.dhdt.index], -self.dhdt, marker=".", linestyle=" ", color="k"
        )
        plt.plot(wt.loc[self.dhdt.index], -dhdt_est, color="C1")

        ax.set_xlabel("Water table (m asl)")
        ax.set_ylabel("$-dh/dt$ [L/T]")

        return ax
