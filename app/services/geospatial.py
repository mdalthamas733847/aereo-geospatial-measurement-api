import json
from pathlib import Path
from typing import Iterable, List

from pyproj import Geod
from shapely.geometry import GeometryCollection, shape
from shapely.ops import unary_union

WGS84 = Geod(ellps="WGS84")


class GeospatialError(ValueError):
    """Raised when a geospatial file cannot be parsed or measured."""


def _extract_geometries(payload) -> List:
    if not isinstance(payload, dict):
        raise GeospatialError("The file must contain a valid GeoJSON object.")

    geo_type = payload.get("type")

    if geo_type == "FeatureCollection":
        geometries = []
        for feature in payload.get("features", []):
            if not isinstance(feature, dict):
                continue
            geometry = feature.get("geometry")
            if geometry:
                geometries.append(shape(geometry))
        return geometries

    if geo_type == "Feature":
        geometry = payload.get("geometry")
        if not geometry:
            raise GeospatialError("GeoJSON Feature has no geometry.")
        return [shape(geometry)]

    if geo_type:
        return [shape(payload)]

    raise GeospatialError("Unsupported or missing GeoJSON type.")


def parse_geojson(raw: bytes) -> List:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GeospatialError("Invalid UTF-8 or malformed JSON.") from exc

    try:
        geometries = _extract_geometries(payload)
    except Exception as exc:
        raise GeospatialError(f"Invalid geometry: {exc}") from exc

    return _validate_geometries(geometries)


def parse_kml(raw: bytes) -> List:
    # Optional KML support. fastkml is deliberately imported here so
    # the API can still start even if KML support is not being used.
    try:
        from fastkml import kml
    except ImportError as exc:
        raise GeospatialError(
            "KML support is unavailable. Install the dependencies from requirements.txt."
        ) from exc

    try:
        document = kml.KML.from_string(raw)
    except Exception as exc:
        raise GeospatialError("Malformed KML file.") from exc

    geometries = []

    def walk(features: Iterable):
        for item in features:
            if getattr(item, "geometry", None) is not None:
                geometries.append(item.geometry)
            children = getattr(item, "features", None)
            if children:
                walk(list(children))

    walk(list(document.features()))
    return _validate_geometries(geometries)


def _validate_geometries(geometries: List) -> List:
    cleaned = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        if geometry is not None and not geometry.is_empty:
            cleaned.append(geometry)

    if not cleaned:
        raise GeospatialError("No valid non-empty geometries were found.")

    return cleaned


def parse_file(filename: str, raw: bytes) -> List:
    suffix = Path(filename).suffix.lower()
    if suffix in {".geojson", ".json"}:
        return parse_geojson(raw)
    if suffix == ".kml":
        return parse_kml(raw)
    raise GeospatialError(
        "Unsupported file type. Upload a .geojson, .json or .kml file."
    )


def _polygon_area_perimeter(geometry):
    # Geod.geometry_area_perimeter supports Polygon and MultiPolygon.
    area, perimeter = WGS84.geometry_area_perimeter(geometry)
    return abs(area), abs(perimeter)


def _line_length(geometry):
    if geometry.geom_type == "LineString":
        length = WGS84.geometry_length(geometry)
        return abs(length)

    if geometry.geom_type == "MultiLineString":
        return sum(abs(WGS84.geometry_length(part)) for part in geometry.geoms)

    return None


def measure(geometries: List) -> dict:
    geometry_collection = GeometryCollection(geometries)
    geometry_types = sorted({g.geom_type for g in geometries})

    polygon_geometries = [
        g for g in geometries
        if g.geom_type in {"Polygon", "MultiPolygon"}
    ]
    line_geometries = [
        g for g in geometries
        if g.geom_type in {"LineString", "MultiLineString"}
    ]

    area_sq_m = None
    perimeter_m = None
    length_m = None

    if polygon_geometries:
        polygon_union = unary_union(polygon_geometries)
        area_sq_m, perimeter_m = _polygon_area_perimeter(polygon_union)

    if line_geometries:
        length_m = sum(_line_length(g) or 0.0 for g in line_geometries)

    if polygon_geometries and line_geometries:
        geometry_type = "Mixed"
    elif len(geometry_types) == 1:
        geometry_type = geometry_types[0]
    else:
        geometry_type = "Mixed"

    return {
        "geometry_type": geometry_type,
        "feature_count": len(geometries),
        "area_sq_m": round(area_sq_m, 4) if area_sq_m is not None else None,
        "perimeter_m": round(perimeter_m, 4) if perimeter_m is not None else None,
        "length_m": round(length_m, 4) if length_m is not None else None,
        "geometry_bounds": list(geometry_collection.bounds),
    }
