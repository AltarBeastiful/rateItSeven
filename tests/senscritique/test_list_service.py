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
import time

from rateItSeven.senscritique.domain.sc_list import ListType, ScList
from rateItSeven.senscritique.list_service import ListService
from tests.lib.test_case import RateItSevenTestCase


class TestListService(RateItSevenTestCase):

    def test_create_list(self):
        user = self.authentified_user()
        listsrv = ListService(user=user)
        sc_list = listsrv.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)
        self.assertIsNotNone(sc_list.path)

    def test_build_list_search_url_no_type(self):
        user = self.authentified_user()
        listsrv = ListService(user=user)
        url = listsrv._build_list_search_url()
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/all/titre/page-1.ajax", url)

    def test_build_list_search_url_movie(self):
        user = self.authentified_user()
        listsrv = ListService(user=user)
        url = listsrv._build_list_search_url(list_type=ListType.MOVIE)
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/films/titre/page-1.ajax", url)

    def test_find_list_find_some(self):
        listsrv = ListService(user=self.authentified_user())

        lists = listsrv.find_list("find_", ListType.MOVIE)
        self.assertCountGreater(lists, 12, "Check if there is still more than 12 list with name like 'find_xxx', if not please create them again.")

    def test_find_list_find_created_one(self):
        service = ListService(user=self.authentified_user())

        unique_name = str(datetime.datetime.now())
        service.create_list(unique_name, ListType.MOVIE)
        # wait 2sec so SensCritique can aknowledge newly created lists
        time.sleep(2)

        lists = list(service.find_list(unique_name, ListType.MOVIE))
        self.assertEqual(1, len(lists))

        # @todo Helper to create and cleanup a list?
        # Clean up created list
        service.delete_list(list=lists[0])

    def test_find_list_find_none(self):
        user = self.authentified_user()
        listsrv = ListService(user=user)
        lists = listsrv.find_list("YoucannotFindme0987654321123", ListType.MOVIE)
        self.assertIsNone(next(lists, None))

    def test_delete_list(self):
        service = ListService(user=self.authentified_user())
        unique_name = "Tobedeleted%s" % (str(datetime.datetime.now()))
        sc_list = service.create_list(unique_name, ListType.MOVIE)

        delete_response = service.delete_list(list=sc_list)

        self.assertTrue(delete_response)
        self.assertEqual([], list(service.find_list(title=unique_name, list_type=ListType.MOVIE)))

    def test_delete_unknown_list_returns_true(self):
        service = ListService(user=self.authentified_user())
        sc_list = ScList(type=ListType.MOVIE, name="unknown", path="list/unknown/12345")

        self.assertTrue(service.delete_list(list=sc_list))

    def test_add_movie(self):
        service = ListService(user=self.authentified_user())
        sc_list = service.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)

        response = service.add_movie(sc_list.compute_list_id(), "11267022", "Un film porno ?")

        self.assertIsNotNone(response)

    def test_add_episode_serie_not_yet_added(self):
        service = ListService(user=self.authentified_user())
        sc_list = service.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)

        response = service.add_episode(sclist=sc_list, product_id="444509", description="S04E01")

        self.assertIsNotNone(response)

    def test_add_episode_serie_already_added(self):
        service = ListService(user=self.authentified_user())
        sc_list = service.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)

        service.add_episode(sclist=sc_list, product_id="444509", description="S04E01")
        service.add_episode(sclist=sc_list, product_id="444509", description="S04E02")

        list_item = service.find_list_item(sclist=sc_list, product_id="444509")
        self.assertIn("S04E01",list_item.description)
        self.assertIn("S04E02",list_item.description)