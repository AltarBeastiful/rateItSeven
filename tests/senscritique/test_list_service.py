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
import datetime

from rateItSeven.senscritique.domain.product import ProductType, Product
from rateItSeven.senscritique.domain.sc_list import ListType, ScList
from rateItSeven.senscritique.list_service import ListService
from tests.lib.test_case import RateItSevenTestCase


class TestListService(RateItSevenTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = ListService(user=RateItSevenTestCase.authentified_user())
        cls.unique_list = cls.service.create_list(str(datetime.datetime.now()), ListType.MOVIE)

    @classmethod
    def tearDownClass(cls):
        cls.service.delete_list(cls.unique_list)

    def test_create_list(self):
        sc_list = self.service.create_list("myList_" + str(datetime.datetime.now()), ListType.MOVIE)
        self.assertIsNotNone(sc_list.path)

    def test_build_list_search_url_no_type(self):
        url = self.service._build_list_search_url()
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/all/titre/page-1.ajax", url)

    def test_build_list_search_url_movie(self):
        url = self.service._build_list_search_url(list_type=ListType.MOVIE)
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/films/titre/page-1.ajax", url)

    def test_find_list_find_some(self):
        lists = self.service.find_list("find_", ListType.MOVIE)
        self.assertCountGreater(lists, 12, "Check if there is still more than 12 list with name like 'find_xxx', if not please create them again.")

    def test_find_list_find_created_one(self):
        lists = list(self.service.find_list(self.unique_list.name, self.unique_list.type))
        self.assertEqual(1, len(lists))

    def test_find_list_find_none(self):
        lists = self.service.find_list("YoucannotFindme0987654321123", ListType.MOVIE)
        self.assertIsNone(next(lists, None))

    def test_delete_list(self):
        unique_name = "Tobedeleted%s" % (str(datetime.datetime.now()))
        sc_list = self.service.create_list(unique_name, ListType.MOVIE)

        delete_response = self.service.delete_list(list=sc_list)

        self.assertTrue(delete_response)
        self.assertEqual([], list(self.service.find_list(title=unique_name, list_type=ListType.MOVIE)))

    def test_delete_unknown_list_returns_true(self):
        sc_list = ScList(type=ListType.MOVIE, name="unknown", path="list/unknown/12345")
        self.assertTrue(self.service.delete_list(list=sc_list))

    def test_add_movie(self):
        response = self.service.add_movie(self.unique_list.compute_list_id(), "11267022", "Un film porno ?")
        self.assertIsNotNone(response)

    def test_remove_movie(self):
        sc_list = self.service.create_list("myList_" + str(datetime.datetime.now()), ListType.MOVIE)
        item_id = self.service.add_movie(sc_list.compute_list_id(), "11267022")
        removed = self.service.remove_movie(sc_list.compute_list_id(), item_id)
        self.assertTrue(removed)

    def test_update_movie(self):
        item_id = self.service.add_movie(self.unique_list.compute_list_id(), "11267022", "Some/path")
        updated = self.service.update_movie(item_id, "Some/other/path")

        self.assertTrue(updated)

        list_item = self.service.find_list_item(self.unique_list, "11267022")
        self.assertEqual("Some/other/path", list_item.description)

    def test_add_episode_serie_not_yet_added(self):
        response = self.service.add_episode(sclist=self.unique_list, product_id="444509", description="S04E01")
        self.assertIsNotNone(response)

    def test_add_episode_serie_already_added(self):
        self.service.add_episode(sclist=self.unique_list, product_id="444509", description="S04E01")
        self.service.add_episode(sclist=self.unique_list, product_id="444509", description="S04E02")

        list_item = self.service.find_list_item(sclist=self.unique_list, product_id="444509")
        self.assertIn("S04E01",list_item.description)
        self.assertIn("S04E02",list_item.description)

    def test_should_find_all_list_items(self):
        sc_list = next(self.service.find_list(title="DONOTCHANGE_list_with_items", list_type=ListType.MOVIE))

        item_list = list(self.service.list_item_list(sc_list=sc_list))

        self.assertEqual(Product(id="373249", title="Izo", type=ProductType.MOVIE), item_list[0].product)
        self.assertEqual("a description", item_list[0].description)

        # We retrieved more than one page
        self.assertCountGreater(item_list, 30)

    def test_find_list_item_on_second_page(self):
        sc_list = next(self.service.find_list(title='DONOTCHANGE_list_with_items', list_type=ListType.MOVIE))

        list_item = self.service.find_list_item(sclist=sc_list, product_id='467126')
        self.assertEqual(Product(id='467126', title='Dead Man', type=ProductType.MOVIE), list_item.product)
