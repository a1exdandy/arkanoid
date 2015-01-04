__author__ = 'alexdandy'

import unittest
import geometry


class TestGeometry(unittest.TestCase):

    def test_intersect_circle_line(self):
        a = geometry.Vector(1, 3)
        b = geometry.Vector(3, 4)
        c = geometry.Vector(-1, 5)
        d = geometry.Vector(6, 1)

        print(geometry.intersect_sector_sector(a, b, c, d))



