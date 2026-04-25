import os

import nibabel as nib
from nibabel.filebasedimages import ImageFileError
from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import NIFTI_EXTENSIONS
from voxelkit.core.types import NiftiMetadataResult
from voxelkit.core.validation import require_supported_extension



def inspect(file_path: str) -> NiftiMetadataResult:
    """Inspect a NIfTI file and return metadata.

    Inputs:
        file_path: Path to a .nii or .nii.gz file.

    Output:
        Dict with filename, shape, ndim, voxel_size, and dtype.

    Extension:
        Add NIfTI-specific metadata behavior in this module only.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=NIFTI_EXTENSIONS,
        message="Unsupported file type. Please provide a .nii or .nii.gz file.",
    )

    filename = os.path.basename(file_path)

    try:
        image = nib.load(file_path)
    except ImageFileError as exc:
        raise ValidationError("Invalid or corrupted NIfTI file.") from exc

    shape = image.shape
    ndim = len(shape)
    zooms = image.header.get_zooms()

    return {
        "filename": filename,
        "shape": list(shape),
        "ndim": ndim,
        "voxel_size": [float(value) for value in zooms[:ndim]],
        "dtype": str(image.get_data_dtype()),
    }
