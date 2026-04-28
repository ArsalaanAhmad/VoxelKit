---
description: VoxelKit REST API overview — start the FastAPI server and call inspect, preview, and report endpoints over HTTP.
---

# REST API

VoxelKit ships with a FastAPI server. It exposes the same inspect, preview, and report operations as the CLI and Python library — but over HTTP, so you can call them from any language or service.

---

## Starting the server

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`.

!!! tip "Interactive docs"
    FastAPI generates Swagger UI automatically. Open `http://127.0.0.1:8000/docs` in your browser to try every endpoint interactively without writing any code.

---

## Health check

```
GET /health
```

Returns `{"status": "ok"}` if the server is running. Useful as a liveness probe.

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

---

## Endpoint overview

All endpoints accept `multipart/form-data` file uploads. JSON endpoints return `application/json`. Preview endpoints return `image/png`.

| Endpoint | Method | Returns | Page |
|---|---|---|---|
| `/nifti/metadata` | POST | JSON metadata | [→](nifti.md) |
| `/nifti/preview` | POST | PNG image | [→](nifti.md) |
| `/h5/inspect` | POST | JSON metadata | [→](h5.md) |
| `/h5/slice` | POST | PNG image | [→](h5.md) |
| `/tiff/metadata` | POST | JSON metadata | [→](tiff.md) |
| `/tiff/preview` | POST | PNG image | [→](tiff.md) |
| `/tiff/report` | POST | JSON QA report | [→](tiff.md) |
| `/embedding/report` | POST | JSON QA report | [→](embedding.md) |
| `/embedding/preview` | POST | PNG heatmap | [→](embedding.md) |
| `/health` | GET | `{"status":"ok"}` | above |

---

## General request pattern

Every endpoint takes a file upload. For JSON responses:

```bash
curl -X POST http://127.0.0.1:8000/nifti/metadata \
  -F "file=@scan.nii.gz"
```

For PNG responses, save to a file:

```bash
curl -X POST "http://127.0.0.1:8000/nifti/preview?plane=axial" \
  -F "file=@scan.nii.gz" \
  --output preview.png
```

---

## Error responses

| Status | Meaning |
|---|---|
| `400` | Bad request — wrong file type, missing required parameter, invalid input |
| `500` | Server error — the file could not be processed |
