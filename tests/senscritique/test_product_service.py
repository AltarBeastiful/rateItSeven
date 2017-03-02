#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2015, Paolo de Vathaire <paolo.devathaire@gmail.com>
#
#   RateItSeven is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   RateItSeven is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with RateItSeven. If not, see <http://www.gnu.org/licenses/>.
#
from rateItSeven.senscritique.domain.product import ProductType, Product
from rateItSeven.senscritique.product_service import ProductService
from tests.lib.test_case import RateItSevenTestCase


class TestProductService(RateItSevenTestCase):

    def test_find_product_no_filter(self):
        products = ProductService().find_product("The Big")
        expected = Product(type=ProductType.MOVIE, title="The Big Lebowski (1998)", id="454350")
        self.assertIn(expected, products)

    def test_find_product_filtering(self):
        products = ProductService().find_product("The Big", ProductType.SERIE)
        unexpected = Product(type=ProductType.MOVIE, title="The Big Lebowski (1998)", id="454350")
        self.assertNotIn(unexpected, products)
