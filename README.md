# Aereo Geospatial File Measurement API

A production-style backend assignment for an **Intern – Software Development Engineer** role.

The API accepts GeoJSON/KML files and calculates geospatial measurements such as:

- Polygon area in square meters
- Polygon perimeter in meters
- LineString/MultiLineString length in meters
- Feature count
- Geometry type
- Measurement history stored in SQLite

## Why this project

The implementation focuses on the engineering skills requested by Aereo:

- Python
- REST API design
- SQL/database persistence
- OOP/service separation
- Input validation
- Error handling
- Git/GitHub readiness
- Automated tests
- Clean maintainable project structure

## Architecture

```text
Client
  |
  | multipart/form-data
  v
FastAPI
  |
  +--> Validation / file-size checks
  |
  +--> Geospatial parser
  |       |
  |       +--> GeoJSON
  |       +--> KML
  |
  +--> Shapely geometry processing
  |
  +--> PyProj WGS84 geodesic calculations
  |
  +--> SQLAlchemy
          |
          v
       SQLite
```

## API Endpoints

### Health

`GET /api/v1/health`

Response:

```json
{
  "status": "healthy"
}
```

### Measure a file

`POST /api/v1/measure`

Upload a `.geojson`, `.json`, or `.kml` file.

Example response:

```json
{
  "id": 1,
  "filename": "sample_polygon.geojson",
  "file_type": "geojson",
  "geometry_type": "Polygon",
  "feature_count": 1,
  "area_sq_m": 12000.1234,
  "perimeter_m": 438.2231,
  "length_m": null,
  "status": "success",
  "error_message": null,
  "created_at": "2026-10-08T12:00:00"
}
```

### List previous measurements

`GET /api/v1/measurements?limit=20`

### Get one measurement

`GET /api/v1/measurements/{measurement_id}`

## Run locally

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Test with curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/measure" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/sample_polygon.geojson"
```

## Run tests

```bash
pytest -q
```

## Docker

Build:

```bash
docker build -t aereo-geospatial-api .
```

Run:

```bash
docker run -p 8000:8000 aereo-geospatial-api
```

Then open:

http://127.0.0.1:8000/docs

## Design decisions

### 1. Geodesic measurements

GeoJSON coordinates are normally longitude/latitude values. Directly treating those coordinates as planar meters would produce incorrect measurements.

This project uses **PyProj's WGS84 geodesic calculations** for length, area and perimeter.

### 2. Separation of concerns

- `routes.py` handles HTTP concerns.
- `geospatial.py` handles parsing and measurement logic.
- `models.py` handles database persistence.
- `schemas.py` defines API response contracts.
- `database.py` manages SQLAlchemy sessions.

This makes the measurement logic independently testable.

### 3. File limits

Uploads are limited to 10 MB to prevent accidental resource exhaustion.

### 4. Invalid geometry

Invalid or empty geometries are rejected. Where possible, a geometry is repaired using a zero-width buffer before measurement.

### 5. Extensibility

The parser can be extended later for additional formats such as Shapefile, GeoTIFF or other GIS formats without changing the HTTP layer.

## Possible production improvements

For a production deployment, I would add:

1. PostgreSQL + PostGIS instead of SQLite.
2. Authentication and role-based authorization.
3. Object storage such as S3/Azure Blob for uploaded files.
4. Async/background processing for very large files.
5. Rate limiting.
6. Structured logging and request IDs.
7. Prometheus/Grafana monitoring.
8. CI/CD through GitHub Actions.
9. API versioning and OpenAPI governance.
10. More extensive geospatial validation and CRS support.

## Project structure

```text
aereo-geospatial-measurement-api/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   └── geospatial.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── sample_data/
│   ├── sample_line.geojson
│   └── sample_polygon.geojson
├── tests/
│   ├── test_api.py
│   └── test_geospatial.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Suggested GitHub commit sequence

Do not upload the project as one giant commit. A clean history can demonstrate your engineering process:

```text
Initial FastAPI project setup
Add geospatial parsing and measurement service
Add measurement persistence with SQLAlchemy
Add REST endpoints and validation
Add automated tests and sample GeoJSON
Add Docker support and documentation
```

## Important submission note

Before submitting, replace/add your own:

- GitHub repository URL
- Your name in the README if desired
- Any screenshots of Swagger UI
- Test results
- Optional architecture diagram

Do not claim production deployment unless you actually deploy it.
