from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aereo Geospatial File Measurement API",
    description=(
        "Production-style REST API for uploading GeoJSON/KML geospatial files "
        "and calculating geodesic distance, perimeter and area."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["System"])
def root():
    return {
        "name": "Aereo Geospatial File Measurement API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
