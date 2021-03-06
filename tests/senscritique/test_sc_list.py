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
import unittest

from rateItSeven.senscritique.domain.sc_list import ScList, ListType


class TestScList(unittest.TestCase):

    def test_compute_list_id(self):
        sclist = ScList(type=ListType.MOVIE, name="A name", path="liste/a_name/1624343")
        self.assertEqual("1624343", sclist.compute_list_id())

    def test_compute_list_id_slash_start(self):
        sclist = ScList(type=ListType.MOVIE, name="A name", path="/liste/a_name/1624343")
        self.assertEqual("1624343", sclist.compute_list_id())

    def test_should_construct_page_url(self):
        sclist = ScList(type=ListType.MOVIE, name="A name", path="/liste/a_name/1622651")

        self.assertEqual("/sc2/liste/1622651/page-1.ajax", sclist.page_url(index=1))
