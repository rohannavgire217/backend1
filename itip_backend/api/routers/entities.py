from typing import List

import geoalchemy2.functions as ST
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

try:
    from itip_backend.api.dependencies import get_current_user
    from itip_backend.db.models import CandidateFacility, ThermalEntity, User
    from itip_backend.db.session import get_db
    from itip_backend.schemas.entity import EntityResponse
except ImportError:  # pragma: no cover
    from api.dependencies import get_current_user
    from db.models import CandidateFacility, ThermalEntity, User
    from db.session import get_db
    from schemas.entity import EntityResponse

router = APIRouter()


@router.get("", response_model=List[EntityResponse])
def get_entities(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(
        ThermalEntity.id,
        ST.ST_Y(ThermalEntity.geom).label("latitude"),
        ST.ST_X(ThermalEntity.geom).label("longitude"),
        ThermalEntity.created_at,
        ThermalEntity.updated_at,
    )

    if current_user.role == "facility_operator":
        if not current_user.osm_facility_id:
            raise HTTPException(status_code=403, detail="No facility assigned to operator.")

        query = query.join(CandidateFacility).filter(
            CandidateFacility.osm_id == current_user.osm_facility_id
        )

    rows = query.order_by(ThermalEntity.created_at.desc()).limit(limit).all()

    return [
        EntityResponse(
            id=row.id,
            latitude=round(row.latitude, 2) if current_user.role == "public" else row.latitude,
            longitude=round(row.longitude, 2) if current_user.role == "public" else row.longitude,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]