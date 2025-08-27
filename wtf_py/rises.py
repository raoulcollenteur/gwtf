
from pandas import DataFrame, IntervalIndex, Series


class RISE:
    def __init__(self):
        """__init__ _summary_
        """
        self.name = "RISE"
        self.nparam = 0
        self.parameters = None

    def get_rises(self, wt) -> DataFrame:
        """Method to get the rises from the water table data.

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
        dtint = IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

        changes = DataFrame(index=dtint, data=dh.values)

        # Only keep the rises that are positive
        rises = changes[changes.values > 0]
        return rises


class MCR:
    def __init__(self):
        """__init__ _summary_
        """
        self.name = "MCR"
        self.nparam = 0
        self.parameters = None

    def get_rises(self, wt, rise_rule="both") -> DataFrame:
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

        Notes
        -----
        This method is not implemented yet.
        """
        # 1. Get the points for which to consider the rises
        events_int= self.get_recharge_sections(wt, rise_rule=rise_rule)

        # 2. Extrapolate using the MCR
        extrapolated = self.get_extrapolated(wt, events_int)

        # 3. Compute the rises
        rises = DataFrame(index=events_int, data=wt[events_int.right].values - extrapolated.values)

        # 4. Return the rises
        return rises

    def get_recharge_sections(self, wt: Series, rise_rule="both") -> DataFrame:
        """Internal method to get the rise sections of the water table fluctuations.

        Parameters
        ----------
        wt : pd.Series
            Time series of the water table fluctuations.

        Returns
        -------
        pd.IntervalIndex
            IntervalIndex with the rise sections of the water table fluctuations.

        """
        dt = wt.index.diff()[1:]
        dh = wt.diff()[1:]

        # Create an IntervalIndex for which the rises are computed
        dtint = IntervalIndex.from_arrays(left=dh.index - dt, right=dh.index)

        changes = DataFrame(index=dtint, data=dh.values)

        # 1. Get the points for which to consider the rises
        if rise_rule not in ["both", "rises"]:
            raise ValueError("rise_rule should be 'both' or 'rises'.")

        # Get only the rise sections
        if rise_rule == "rises":
            return changes[changes.values > 0].index
        # Get every point
        elif rise_rule == "both":
            return changes.index


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

        return dhdt

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

        pass

    def get_extrapolated(self, wt: Series, events: IntervalIndex) -> Series:
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
        # For now, return the original values
        return wt[events.left]

