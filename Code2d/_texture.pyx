#from Phuong Pham - 18.02.2022 based on a code-file of skikit-image

import numpy as np
cimport numpy as cnp
from libc.math cimport sin, cos, abs

cimport numpy as cnp
import numpy as np

ctypedef fused np_floats:
    cnp.float32_t
    cnp.float64_t
ctypedef fused np_ints:
    cnp.int8_t
    cnp.int16_t
    cnp.int32_t
    cnp.int64_t

ctypedef fused np_uints:
    cnp.uint8_t
    cnp.uint16_t
    cnp.uint32_t
    cnp.uint64_t
ctypedef fused np_anyint:
    np_uints
    np_ints

cdef extern from "numpy/npy_math.h":
    double NAN "NPY_NAN"

cdef inline Py_ssize_t round(np_floats r) nogil:
    return <Py_ssize_t>(
        (r + <np_floats>0.5) if (r > <np_floats>0.0) else (r - <np_floats>0.5)
    )

cnp.import_array()

def _glcm_loop(np_anyint[:, ::1] image, double[:] distances,
               double[:] angles, Py_ssize_t levels,
               cnp.uint32_t[:, :, :, ::1] out):
    """Perform co-occurrence matrix accumulation.

    Parameters
    ----------
    image : ndarray
        Integer typed input image. Only positive valued images are supported.
        If type is other than uint8, the argument `levels` needs to be set.
    distances : ndarray
        List of pixel pair distance offsets.
    angles : ndarray
        List of pixel pair angles in radians.
    levels : int
        The input image should contain integers in [0, `levels`-1],
        where levels indicate the number of gray-levels counted
        (typically 256 for an 8-bit image).
    out : ndarray
        On input a 4D array of zeros, and on output it contains
        the results of the GLCM computation.

    """

    cdef:
        Py_ssize_t a_idx, d_idx, r, c, rows, cols, row, col, start_row,\
                   end_row, start_col, end_col, offset_row, offset_col
        np_anyint i, j
        cnp.float64_t angle, distance

    with nogil:
        rows = image.shape[0]
        cols = image.shape[1]

        for a_idx in range(angles.shape[0]):
            angle = angles[a_idx]
            for d_idx in range(distances.shape[0]):
                distance = distances[d_idx]
                offset_row = round(sin(angle) * distance)
                offset_col = round(cos(angle) * distance)
                start_row = max(0, -offset_row)
                end_row = min(rows, rows - offset_row)
                start_col = max(0, -offset_col)
                end_col = min(cols, cols - offset_col)
                for r in range(start_row, end_row):
                    for c in range(start_col, end_col):
                        i = image[r, c]
                        row = r + offset_row
                        col = c + offset_col
                        j = image[row, col]
                        if 0 <= i < levels and 0 <= j < levels:
                            out[i, j, d_idx, a_idx] += 1

