import numpy as np
import os
import pytest
import math

import perturbopy.postproc as ppy

points_cryst = [[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]]
points_cart = [[0, 0, 0.5, 0.5,  0.25, 0.75], [0, 1, 0.5, 1,   1,   0.75], [0,   0,   0.5, 0,   0.25,0.]]

@pytest.fixture()
def recip_dbs():
    
    return ppy.RecipPtDB(points_cart, points_cryst, units='cryst')


# # Test constructor

# # Test from_lattice


# kpts_db2 = KptsDB.from_lattice(kpts_cryst, 'cryst', lat, recip_lat)
# kpts_db2 = ppy.KptsDB.from_lattice(kpts_cryst, 'cryst', lat, recip_lat)
# assert(np.all(kpts_db2.kpts_cryst == vectors_cryst))
# assert(np.all(kpts_db2.kpts_cart == vectors_cart))
# assert(kpts_db2.units == 'crystal')   # def from_lattice(self, kpts, units, lat, recip_lat, kpath=None, kpath_units='arbitrary', labels=None):
# assert(kpts_db.units == 'crystal')
# assert(kpts_db._units == 'crystal')
# kpts_db.units = 'cart'
# assert(kpts_db.units == 'tpiba')
# assert(kpts_db.units == 'cartesian')

# Test units and points properties
@pytest.mark.parametrize("units_input, expected_units, expected_points", [
	('cryst', 'crystal', points_cryst), ('Cartesian', 'cartesian', points_cart),
	])
def test_properties(recip_dbs, units_input, expected_units, expected_points):

	recip_dbs.units = units_input
	assert(recip_dbs.units == expected_units)
	assert(np.all(recip_dbs.points == expected_points))

# Test scale_path
@pytest.mark.parametrize("test_min, test_max, expected", [
	(0,1,[0,0.2,0.4,0.6,0.8,1])
	])
def test_scale_path(recip_dbs, test_min, test_max, expected):
	recip_dbs.scale_path(test_min, test_max)
	print(type(recip_dbs))
	assert(np.all(recip_dbs.path == expected))

# Test distances
@pytest.mark.parametrize("point, expected", [
	([[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]], [0, 0, 0, 0, 0, 0]),
	# ([[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]], [0,0,0]),
	])
def test_compute_distances(recip_dbs, point,expected):
	print(recip_dbs.distances(point))
	assert(np.all(np.isclose(recip_dbs.distances(point), expected)))

# Test where
@pytest.mark.parametrize("test_point, atol, expected", [
	([0,0,0], None, 0), ([0.25, 0.625, 0.625], None, 4),
	([0.25, 0.625, 0.56], None, None), ([0.25, 0.625, 0.56], 0.1, 4),
	([0, 0.5, 0.5], None, [1]),
	# ([0.25, 0.25, 0.25], 0.6, [1])
	])
def test_where(recip_dbs, test_point, atol, expected):
	print(recip_dbs.distances(test_point))
	print(recip_dbs.where(test_point))
	if atol is None:
		assert(np.all(recip_dbs.where(test_point) == expected))
	else:
		assert(np.all(recip_dbs.where(test_point, atol=atol) == expected))

# # Test point to path
# @pytest.mark.parametrize("test_point, atol, expected", [
# 	([0,0,0], None, 0), ([0.25, 0.625, 0.625], None, 4),
# 	([0.25, 0.625, 0.56], None, None), ([0.25, 0.625, 0.56], 0.1, 4),
# 	])
# def test_point_to_path(recip_dbs, test_point, atol, expected):
	
# 	if atol is None:
# 		assert(np.all(recip_dbs.point_to_path(test_point) == expected))
# 	else:
# 		print(recip_dbs.where(test_point, atol=atol))
# 		assert(np.all(recip_dbs.point_to_path(test_point, atol=atol) == expected))

# # Test path to point
# @pytest.mark.parametrize("test_path, test_points_array, test_path_array, atol, expected", [
# 	(),
# 	])
# def test_path_to_point(test_path, test_points_array, test_path_array, atol, expected):
#     assert(ppy.lattice.path_to_point(test_path, test_points_array, test_path_array))
