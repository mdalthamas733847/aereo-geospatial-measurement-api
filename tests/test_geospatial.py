import json

from app.services.geospatial import measure, parse_geojson


def polygon_geojson():
    return json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Test Area"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [77.5946, 12.9716],
                        [77.5956, 12.9716],
                        [77.5956, 12.9726],
                        [77.5946, 12.9726],
                        [77.5946, 12.9716]
                    ]]
                }
            }
        ]
    }).encode()


def test_parse_geojson():
    geometries = parse_geojson(polygon_geojson())
    assert len(geometries) == 1
    assert geometries[0].geom_type == "Polygon"


def test_measure_polygon():
    geometries = parse_geojson(polygon_geojson())
    result = measure(geometries)
    assert result["feature_count"] == 1
    assert result["geometry_type"] == "Polygon"
    assert result["area_sq_m"] is not None
    assert result["area_sq_m"] > 0
    assert result["perimeter_m"] is not None
    assert result["perimeter_m"] > 0
