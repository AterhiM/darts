import unittest
import pandas as pd
import numpy as np

from ..timeseries import TimeSeries
from ..utils.missing_values import auto_fillna, na_ratio


class MissingValuesTestCase(unittest.TestCase):

    time = pd.date_range('20130101', '20130130')
    lin = [float(i) for i in range(len(time))]
    cub = [float(i - 4) ** 2 for i in range(len(time))]
    series1: TimeSeries = TimeSeries.from_times_and_values(time, np.array([2.0] * len(time)))
    series2: TimeSeries = TimeSeries.from_times_and_values(time, np.array(lin))
    series3: TimeSeries = TimeSeries.from_times_and_values(time, np.array([10] * 10 + lin[-20:]))
    series4: TimeSeries = TimeSeries.from_times_and_values(time, np.array(lin[:20] + [19] * 10))
    series5: TimeSeries = TimeSeries.from_times_and_values(time, np.array(cub))
    series6: TimeSeries = TimeSeries.from_times_and_values(time, [0] * 2 + cub[2:-2] + [-1] * 2)

    def test_fill_constant(self):
        seriesA: TimeSeries = TimeSeries.from_times_and_values(
            self.time,
            np.array([np.nan] * 5 + [2.0] * 5 + [np.nan] * 5 + [2.0] * 10 + [np.nan] * 5)
        )

        # Check that no changes are made if there are no missing values
        self.assertEqual(self.series1, auto_fillna(self.series1))

        # Check that a constant function is filled to a constant function
        self.assertEqual(self.series1, auto_fillna(seriesA))

    def test_linear(self):
        seriesB: TimeSeries = TimeSeries.from_times_and_values(self.time,
                                                               np.array(self.lin[:10] + [np.nan] * 10 + self.lin[-10:]))

        # Check for linear interpolation part
        self.assertEqual(self.series2, auto_fillna(seriesB))

    def test_bfill(self):
        seriesC: TimeSeries = TimeSeries.from_times_and_values(self.time,
                                                               np.array([np.nan] * 10 + self.lin[-20:]))

        # Check that auto-backfill works properly
        self.assertEqual(self.series3, auto_fillna(seriesC))

    def test_ffil(self):
        seriesD: TimeSeries = TimeSeries.from_times_and_values(self.time,
                                                               np.array(self.lin[:20] + [np.nan] * 10))

        self.assertEqual(self.series4, auto_fillna(seriesD))

    def test_fill_quad(self):
        seriesE: TimeSeries = TimeSeries.from_times_and_values(self.time,
                                                               np.array(self.cub[:10] + [np.nan] * 10 + self.cub[-10:]))
        self.assertEqual(self.series5, round(auto_fillna(seriesE, method='quadratic'), 7))

    def test_multivariate_fill(self):
        seriesA: TimeSeries = TimeSeries.from_times_and_values(
            self.time,
            np.array([np.nan] * 5 + [2.0] * 5 + [np.nan] * 5 + [2.0] * 10 + [np.nan] * 5)
        )
        seriesB: TimeSeries = TimeSeries.from_times_and_values(self.time,
                                                               np.array(self.lin[:10] + [np.nan] * 10 + self.lin[-10:]))
        self.assertEqual(self.series1.stack(self.series2), auto_fillna(seriesA.stack(seriesB)))

    def test__na_ratio(self):
        seriesF = TimeSeries.from_times_and_values(self.time, list(range(27)) + [np.nan] * 3)

        # univariate case
        self.assertEqual(na_ratio(seriesF), 0.1)

        # multivariate case
        self.assertEqual(na_ratio(seriesF.stack(seriesF)), 0.1)
