"""
Thyroid nodule size calculator.

Calculates volume and maximum dimension based on 2D or 3D measurements.
"""

from typing import TypedDict, Literal, Optional
import math


class SizeInput(TypedDict, total=False):
    mode: Literal['2d', '3d']
    a_mm: float  # First dimension (typically AP or length)
    b_mm: Optional[float]  # Second dimension (typically TR or width)
    c_mm: Optional[float]  # Third dimension (typically CC or height)


class SizeResult(TypedDict):
    mode: str
    a_mm: float
    b_mm: Optional[float]
    c_mm: Optional[float]
    volume_mm3: Optional[float]
    max_dimension_mm: float


def calculate_size(size_input: SizeInput) -> SizeResult:
    """
    Calculate nodule size metrics.

    For 3D measurements, volume is calculated using the ellipsoid formula:
    V = (pi/6) * a * b * c

    Args:
        size_input: Dictionary containing size mode and measurements

    Returns:
        SizeResult with volume and maximum dimension
    """
    mode = size_input.get('mode', '2d')
    a_mm = size_input.get('a_mm', 0)
    b_mm = size_input.get('b_mm')
    c_mm = size_input.get('c_mm')

    # Calculate max dimension
    dimensions = [a_mm]
    if b_mm is not None:
        dimensions.append(b_mm)
    if c_mm is not None:
        dimensions.append(c_mm)

    max_dimension_mm = max(dimensions) if dimensions else 0

    # Calculate volume for 3D mode
    volume_mm3 = None
    if mode == '3d' and a_mm and b_mm and c_mm:
        # Ellipsoid volume formula: V = (4/3) * pi * (a/2) * (b/2) * (c/2)
        # Simplified: V = (pi/6) * a * b * c
        volume_mm3 = round((math.pi / 6) * a_mm * b_mm * c_mm, 1)

    return {
        'mode': mode,
        'a_mm': a_mm,
        'b_mm': b_mm,
        'c_mm': c_mm,
        'volume_mm3': volume_mm3,
        'max_dimension_mm': max_dimension_mm,
    }
