from typing import List, Optional

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    master: str
    competitors: List[str]
    anchor: str = Field(default="car insurance")
    timeframe: str = Field(default="today 3-m")
    geo: str = Field(default="IE")
    category: Optional[int] = None
    gprop: str = Field(default="")
    repeat: int = Field(default=1, ge=1)
    sleep_seconds: float = Field(default=1.0, ge=0)


class CompetitorResult(BaseModel):
    name: str
    series: List[float]
    relative_strength: float
    raw_score: float
    normalized_score: float
    trend: str


class CompareResponse(BaseModel):
    time_buckets: List[str]
    master_baseline: List[float]
    baseline_average: float
    competitors: List[CompetitorResult]
    warnings: List[str] = []
