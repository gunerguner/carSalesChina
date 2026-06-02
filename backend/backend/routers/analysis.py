from typing import Annotated

from fastapi import APIRouter, Query

from backend.core.decorators import handle_success_response
from backend.core.deps import DbSession
from backend.schemas.analysis import AnalysisTrendQuery
from backend.services import analysis_service

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/nev-share/trend")
@handle_success_response
def nev_share_trend(
    query: Annotated[AnalysisTrendQuery, Query()],
    db: DbSession,
):
    return analysis_service.get_nev_share_trend(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )


@router.get("/nev-breakdown")
@handle_success_response
def nev_breakdown(
    query: Annotated[AnalysisTrendQuery, Query()],
    db: DbSession,
):
    return analysis_service.get_nev_breakdown(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )


@router.get("/origin-share/trend")
@handle_success_response
def origin_share_trend(
    query: Annotated[AnalysisTrendQuery, Query()],
    db: DbSession,
):
    return analysis_service.get_origin_share_trend(
        db=db,
        years=query.years,
        granularity=query.granularity,
    )