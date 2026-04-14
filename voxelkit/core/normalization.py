import numpy as np


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    """Normalize any numeric image array to uint8 in [0, 255].

    Inputs:
        image: Numeric numpy array, usually a 2D slice.

    Output:
        A uint8 numpy array with the same shape.
    """
    image = np.nan_to_num(image, nan=0.0, posinf=0.0, neginf=0.0)
    min_value = float(np.min(image))
    max_value = float(np.max(image))

    if max_value == min_value:
        return np.zeros(image.shape, dtype=np.uint8)

    normalized = (image - min_value) / (max_value - min_value)
    return (normalized * 255.0).astype(np.uint8)
