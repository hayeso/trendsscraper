import time
from typing import List, Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from pytrends.request import TrendReq


def _pytrends_client() -> TrendReq:
    """Create a configured TrendReq client."""
    return TrendReq(hl="en-US", tz=0, retries=2, backoff_factor=0.4,
                    requests_args={"timeout": (10, 25)})


def build_payload_and_fetch(keywords: List[str], timeframe: str, geo: str,
                             category: int | None, gprop: str) -> pd.DataFrame:
    """Fetch interest over time for given keywords."""
    pt = _pytrends_client()
    pt.build_payload(keywords, timeframe=timeframe, geo=geo, cat=category or 0,
                     gprop=gprop)
    df = pt.interest_over_time()
    if 'isPartial' in df.columns:
        df = df.drop(columns=['isPartial'])
    return df


def trimmed_median(values: Iterable[float], trim: float = 0.1) -> float:
    """Return the trimmed median of the provided values."""
    arr = np.array(list(values), dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        return float("nan")
    arr.sort()
    k = int(len(arr) * trim)
    if k > 0:
        arr = arr[k:-k]
    return float(np.median(arr))


def robust_slope(series: pd.Series) -> float:
    """Compute a simple slope of the series using linear regression."""
    if series.empty:
        return 0.0
    y = series.values
    x = np.arange(len(y))
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def _scale_factor(anchor_base: pd.Series, anchor_pair: pd.Series) -> float | None:
    """Compute scaling factor using anchor series."""
    df = pd.concat([anchor_base, anchor_pair], axis=1, join='inner')
    df = df.replace(0, np.nan).dropna()
    if df.empty:
        return None
    ratios = df.iloc[:, 0] / df.iloc[:, 1]
    return trimmed_median(ratios)


def compare_trends(master: str, competitors: List[str], anchor: str,
                    timeframe: str, geo: str, category: int | None,
                    gprop: str) -> Tuple[List[str], pd.Series, List[Dict], List[str]]:
    """
    Perform baseline and pairwise queries then stitch via anchor.
    Returns time buckets, master baseline series, competitor results and warnings.
    """
    baseline_df = build_payload_and_fetch([master, anchor], timeframe, geo, category, gprop)
    m_base = baseline_df[master]
    a_base = baseline_df[anchor]
    time_buckets = baseline_df.index.strftime('%Y-%m-%d').tolist()

    baseline_avg = float(m_base.mean())
    competitor_results: List[Dict] = []
    warnings: List[str] = []

    for comp in competitors:
        pair_df = build_payload_and_fetch([master, comp, anchor], timeframe, geo, category, gprop)
        pair_df = pair_df.reindex(baseline_df.index)
        a_pair = pair_df[anchor]
        m_pair = pair_df[master]
        c_pair = pair_df[comp]

        scale = _scale_factor(a_base, a_pair)
        if scale is None or np.isnan(scale):
            warnings.append(f"Insufficient overlap for {comp}")
            continue
        m_adj = (m_pair * scale).reindex(baseline_df.index)
        c_adj = (c_pair * scale).reindex(baseline_df.index)

        raw_score = float(c_adj.mean())
        rs = raw_score / baseline_avg if baseline_avg else 0.0
        norm_score = rs * 100.0
        slope = robust_slope(c_adj)
        epsilon = max(baseline_avg * 0.01, 0.1)
        if slope > epsilon:
            trend = 'up'
        elif slope < -epsilon:
            trend = 'down'
        else:
            trend = 'stable'

        competitor_results.append({
            'name': comp,
            'series': [float(v) for v in c_adj.values],
            'relative_strength': rs,
            'raw_score': raw_score,
            'normalized_score': norm_score,
            'trend': trend,
        })

    return time_buckets, m_base, competitor_results, warnings
