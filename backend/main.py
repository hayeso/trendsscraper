from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .domain import compare_trends
from .models import CompareRequest, CompareResponse, CompetitorResult

app = FastAPI(title="Trends Compare API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/trends/compare", response_model=CompareResponse)
def trends_compare(req: CompareRequest) -> CompareResponse:
    """Compare master against competitors using Google Trends."""
    try:
        time_buckets, master_baseline, competitors, warnings = compare_trends(
            req.master,
            req.competitors,
            req.anchor,
            req.timeframe,
            req.geo,
            req.category,
            req.gprop,
        )
        return CompareResponse(
            time_buckets=time_buckets,
            master_baseline=[float(v) for v in master_baseline.values],
            baseline_average=float(master_baseline.mean()),
            competitors=[CompetitorResult(**c) for c in competitors],
            warnings=warnings,
        )
    except Exception as exc:  # pragma: no cover - protective layer
        raise HTTPException(status_code=400, detail=str(exc))
