"""The hat monotile (Smith, Myers, Kaplan, Goodman-Strauss 2023) as a shapely polygon.

    EinsteinHat(x, y, deg, flip)  ->  .polygon (shapely), .vertices (13x2 numpy)

(x, y) is the centroid of the hat.  Transform order: flip reflects x -> -x (mirror in the
vertical axis through the centroid), then rotate `deg` degrees counter-clockwise about the
centroid, then translate the centroid to (x, y).  Kite short edge 1, long edge sqrt(3),
area 8*sqrt(3).  Outline: Craig Kaplan's hatviz geometry.js (github.com/isohedral/hatviz),
hexPt(a, b) = (a + b/2, b*sqrt(3)/2), shifted so that the centroid (1.5, 0) sits at the origin.
"""
import numpy as np
from shapely.geometry import Polygon

SQRT3 = np.sqrt(3.0)
AREA = 8.0 * SQRT3                       # exact area of one hat

# hatviz hat_outline, in hex-lattice coordinates (a, b)
HEX_POINTS = [(0, 0), (-1, -1), (0, -2), (2, -2), (2, -1), (4, -2), (5, -1),
              (4, 0), (3, 0), (2, 2), (0, 3), (0, 2), (-1, 2)]
CENTROID_HEX = (1.5, 0.0)                # centroid of the outline above, in Cartesian coordinates

# base hat: 13 Cartesian vertices, centroid at (0, 0), unflipped, 0 degrees
HAT = np.array([(a + 0.5 * b - CENTROID_HEX[0], SQRT3 / 2 * b - CENTROID_HEX[1]) for a, b in HEX_POINTS])
DIAMETER = max(np.linalg.norm(p - q) for p in HAT for q in HAT)   # = 6.0


class EinsteinHat:
    def __init__(self, x=0.0, y=0.0, deg=0.0, flip=False):
        self.x, self.y, self.deg, self.flip = float(x), float(y), float(deg), bool(flip)

    @property
    def vertices(self) -> np.ndarray:
        pts = HAT * np.array([-1.0, 1.0]) if self.flip else HAT
        t = np.radians(self.deg)
        rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])     # counter-clockwise
        return pts @ rot.T + np.array([self.x, self.y])

    @property
    def polygon(self) -> Polygon:
        return Polygon(self.vertices)

    def __repr__(self):
        return f"EinsteinHat(x={self.x}, y={self.y}, deg={self.deg}, flip={self.flip})"
