from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.core.database import get_db
from backend.schemas.analysis import AnalysisTrendQuery
from backend.schemas.response import success
from backend.services import analysis_service

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/nev-share/trend")
def nev_share_trend(
    query: AnalysisTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    data = analysis_service.get_nev_share_trend(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )
    return success(data)


@router.get("/nev-breakdown")
def nev_breakdown(
    query: AnalysisTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    data = analysis_service.get_nev_breakdown(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )
    return success(data)


@router.get("/origin-share/trend")
def origin_share_trend(
    query: AnalysisTrendQuery = Depends(),
    db: Session = Depends(get_db),
):
    data = analysis_service.get_origin_share_trend(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )
    return success(data)