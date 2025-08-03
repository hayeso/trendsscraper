import pandas as pd
from backend.domain import trimmed_median, robust_slope


def test_trimmed_median():
    series = pd.Series([1, 2, 3, 100])
    assert trimmed_median(series, trim=0.25) == 2.5


def test_robust_slope():
    series = pd.Series([1, 2, 3, 4])
    assert abs(robust_slope(series) - 1.0) < 1e-6
