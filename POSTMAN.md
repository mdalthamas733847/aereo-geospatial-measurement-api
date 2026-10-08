# Postman / API Testing Guide

Base URL:

```text
http://127.0.0.1:8000
```

## 1. Health check

GET:

```text
/api/v1/health
```

## 2. Upload GeoJSON

POST:

```text
/api/v1/measure
```

Body → `form-data`

Key:

```text
file
```

Type:

```text
File
```

Select:

```text
sample_data/sample_polygon.geojson
```

## 3. List history

GET:

```text
/api/v1/measurements
```

## 4. Get measurement

GET:

```text
/api/v1/measurements/1
```
