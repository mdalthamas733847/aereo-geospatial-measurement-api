from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    geometry_type: str
    feature_count: int
    area_sq_m: Optional[float] = None
    perimeter_m: Optional[float] = None
    length_m: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
