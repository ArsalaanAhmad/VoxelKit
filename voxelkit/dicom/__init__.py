"""DICOM support — single-file and series-directory inspect / preview / report.

PHI is stripped from every public output by default. See `voxelkit.dicom.phi`
for the scrubbing primitive and `voxelkit.dicom.inspect.inspect(include_phi=...)`
for the read-side opt-in.
"""

from voxelkit.dicom.anonymise import anonymise_directory
from voxelkit.dicom.inspect import inspect
from voxelkit.dicom.preview import preview
from voxelkit.dicom.report import report

__all__ = ["inspect", "preview", "report", "anonymise_directory"]
