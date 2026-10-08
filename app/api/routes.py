from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.schemas import MeasurementResponse
from app.services.geospatial import GeospatialError, measure, parse_file

router = APIRouter()


@router.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}


@router.post(
    "/measure",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Measurements"],
    summary="Upload a geospatial file and calculate measurements",
)
async def create_measurement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    raw = await file.read()

    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum allowed size is 10 MB.",
        )

    try:
        geometries = parse_file(file.filename, raw)
        result = measure(geometries)
    except GeospatialError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record = Measurement(
        filename=file.filename,
        file_type=file.filename.rsplit(".", 1)[-1].lower(),
        geometry_type=result["geometry_type"],
        feature_count=result["feature_count"],
        area_sq_m=result["area_sq_m"],
        perimeter_m=result["perimeter_m"],
        length_m=result["length_m"],
        status="success",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get(
    "/measurements",
    response_model=List[MeasurementResponse],
    tags=["Measurements"],
)
def list_measurements(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    return (
        db.query(Measurement)
        .order_by(Measurement.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/measurements/{measurement_id}",
    response_model=MeasurementResponse,
    tags=["Measurements"],
)
def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(Measurement)
        .filter(Measurement.id == measurement_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Measurement not found.")
    return record
