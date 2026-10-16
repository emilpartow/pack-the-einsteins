"""Geometric facts about the hat that the rest of the kit relies on."""
import numpy as np
from shapely import affinity

from tile import AREA, DIAMETER, HAT, SQRT3, EinsteinHat


def test_tile_area_is_8_sqrt3():
    assert abs(EinsteinHat().polygon.area - 8 * SQRT3) < 1e-12
    assert abs(AREA - 8 * SQRT3) < 1e-12


def test_tile_13_vertices_edge_lengths_1_sqrt3_2():
    assert HAT.shape == (13, 2)
    edges = np.linalg.norm(np.roll(HAT, -1, axis=0) - HAT, axis=1)
    expected = [SQRT3, 1, 2, 1, SQRT3, SQRT3, 1, 1, SQRT3, SQRT3, 1, 1, SQRT3]
    assert np.allclose(edges, expected, atol=1e-12)


def test_tile_valid_simple_after_flip_and_rotate():
    for flip in (False, True):
        for deg in (0, 17.3, 90, 200, -45):
            p = EinsteinHat(1.0, -2.0, deg, flip).polygon
            assert p.is_valid and p.is_simple and len(p.exterior.coords) == 14


def test_centroid_is_reference_point():
    c = EinsteinHat(2.0, -3.0, 37.0).polygon.centroid
    assert abs(c.x - 2.0) < 1e-12 and abs(c.y + 3.0) < 1e-12
    c = EinsteinHat(2.0, -3.0, 37.0, flip=True).polygon.centroid
    assert abs(c.x - 2.0) < 1e-12 and abs(c.y + 3.0) < 1e-12


def test_flip_is_mirror_not_rotation():
    hat, mirror = EinsteinHat().polygon, EinsteinHat(flip=True).polygon
    assert mirror.equals(affinity.scale(hat, -1, 1, origin=(0, 0)))
    for deg in np.arange(0, 360, 0.5):   # no rotation maps the hat onto its mirror image
        assert affinity.rotate(hat, deg, origin=(0, 0)).symmetric_difference(mirror).area > 1e-3


def test_rotation_is_ccw_degrees():
    v0, v90 = EinsteinHat(deg=0).vertices, EinsteinHat(deg=90).vertices
    assert np.allclose(v90[:, 0], -v0[:, 1]) and np.allclose(v90[:, 1], v0[:, 0])
    kaggle_style = affinity.rotate(EinsteinHat().polygon, 90, origin=(0, 0))   # same convention as Kaggle
    assert EinsteinHat(deg=90).polygon.symmetric_difference(kaggle_style).area < 1e-12


def test_diameter_is_6():
    assert abs(DIAMETER - 6.0) < 1e-12
