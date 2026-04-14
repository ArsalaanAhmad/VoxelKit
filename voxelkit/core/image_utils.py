from io import BytesIO

import numpy as np
from PIL import Image



def to_png_bytes(image_2d_uint8: np.ndarray) -> bytes:
    """Convert a 2D uint8 image array into PNG bytes.

    Inputs:
        image_2d_uint8: 2D numpy array with dtype uint8.

    Output:
        PNG-encoded image bytes.
    """
    if image_2d_uint8.ndim != 2:
        raise ValueError("Expected a 2D image array.")

    image = Image.fromarray(image_2d_uint8, mode="L")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
