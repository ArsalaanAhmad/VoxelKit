---
description: voxelkit anonymise — scrub PHI from a directory of DICOM files.
---

# voxelkit anonymise

```bash
voxelkit anonymise <directory> --output <output_directory>
```

Recursively walks a directory tree, opens every `.dcm` file, blanks the patient-identifying tags, and writes the scrubbed copies to a parallel output tree. Non-DICOM files (READMEs, segmentation masks, anything that's not `.dcm`) are skipped — the input tree is never modified.

The pixel data, modality, image geometry, and series-grouping UIDs are preserved so the anonymised dataset stays usable for downstream pipelines.

---

## Usage

```
voxelkit anonymise DIRECTORY --output OUTPUT [--no-recursive]
```

### Arguments

| Argument | Description |
|---|---|
| `DIRECTORY` | Input directory to scan for `.dcm` files |

### Flags

| Flag | Description |
|---|---|
| `--output PATH` | Output directory (required). Created if needed. Mirrors the input tree. |
| `--no-recursive` | Only process `.dcm` files at the top level — don't descend into subdirectories. |

---

## Example

```bash
voxelkit anonymise ./incoming_studies/ --output ./anonymised/
```

Output (stdout JSON summary):

```json
{
  "input_dir": "/data/incoming_studies",
  "output_dir": "/data/anonymised",
  "total_dcm_files": 1248,
  "files_anonymised": 1248,
  "files_failed": 0,
  "failures": [],
  "scrubbed_tag_counts": {
    "AccessionNumber": 1248,
    "InstitutionName": 1248,
    "PatientBirthDate": 1248,
    "PatientID": 1248,
    "PatientName": 1248,
    "StudyDate": 1248,
    "StudyTime": 1248
  }
}
```

`scrubbed_tag_counts` tells you which PHI tags your dataset actually carried — tags that were absent are not included.

---

## What gets scrubbed

The full list lives in [`voxelkit/dicom/phi.py`](https://github.com/ArsalaanAhmad/VoxelKit/blob/main/voxelkit/dicom/phi.py). It covers two categories:

- **Direct identifiers** — patient name, ID, birth date, sex, age, weight, addresses, phone numbers, accession number, referring/operating physicians, institution name and address, device serial number, station name, and similar.
- **Temporal identifiers** — study/series/acquisition/content dates and times, which re-identify trivially when combined with institution and modality info.

Values are replaced with empty strings rather than deleted. The element keeps its tag and VR so the file structure stays DICOM-compliant.

---

## What is *not* scrubbed

- **StudyInstanceUID / SeriesInstanceUID / SOPInstanceUID** — these are random identifiers, not PHI in themselves, and removing them would break the series grouping. If your threat model requires UID regeneration as well, run a UID-replacement step downstream.
- **Pixel data** — burned-in identifiers in the image itself (e.g. a name overlay rendered into the pixel array) are not detected or removed. Visually QA your output if your source dataset is known to carry burned-in PHI.

---

!!! warning "Not a substitute for de-identification certification"
    This command implements a conservative basic-profile scrub. It is not certified for HIPAA Safe Harbor, DICOM PS3.15 Annex E full compliance, or any specific regulatory framework. Treat it as a useful default that you must validate against your own threat model before publishing data.
