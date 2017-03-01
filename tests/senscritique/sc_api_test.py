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
import unittest

from rateItSeven.senscritique.domain.product import Product, ProductType
from rateItSeven.senscritique.sc_api import AuthSrv, ListSrv, ListType, UnauthorizedException, ProductSrv


class TestLoginRequest(unittest.TestCase):
    LIST_NODES_XPATH = '//div[@data-rel="lists-content"]/ul/li'

    def setUp(self):
        self.login = "legalizme@gmail.com"
        self.password = "12345"
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        sc_list = listsrv.create_list("myTestList_"+str(datetime.datetime.now()), ListType.MOVIE)
        self.list_id = sc_list.compute_list_id()

    def tearDown(self):
        # TODO Delete list
        pass

    def test_login_success(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        self.assertNotEqual(0, len(user.session_cookies))
        self.assertEqual("invite-san", user.username)

    def test_login_failure(self):
        with self.assertRaises(UnauthorizedException) as exc_catcher:
            response = AuthSrv().dologin(u"alogin", "badpassword")

    def test_add_movie(self):
        response = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(response)
        response = listsrv.add_movie(self.list_id, "11267022", "Un film porno ?")
        self.assertIsNotNone(response)

    def test_create_list(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        sc_list = listsrv.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)
        self.assertIsNotNone(sc_list.path)

    def test_build_list_search_url_no_type(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        url = listsrv._build_list_search_url()
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/all/titre/page-1.ajax", url)

    def test_build_list_search_url_movie(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        url = listsrv._build_list_search_url(list_type=ListType.MOVIE)
        self.assertEqual("https://www.senscritique.com/sc2/invite-san/listes/all/films/titre/page-1.ajax", url)

    def test_find_list_find_some(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        listsrv.create_list("find_"+str(datetime.datetime.now()), ListType.MOVIE)
        listsrv.create_list("find_"+str(datetime.datetime.now()), ListType.MOVIE)
        # wait 2sec so SensCritique can aknowledge newly created lists
        time.sleep(2)
        lists = listsrv.find_list("find_", ListType.MOVIE)
        self.assertGreater(len(lists), 1)

    def test_find_list_find_one(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        unique_name = str(datetime.datetime.now())
        listsrv.create_list(unique_name, ListType.MOVIE)
        # wait 2sec so SensCritique can aknowledge newly created lists
        time.sleep(2)
        lists = listsrv.find_list(unique_name, ListType.MOVIE)
        self.assertEqual(len(lists), 1)

    def test_find_list_find_none(self):
        user = AuthSrv().dologin(email=self.login, password=self.password)
        listsrv = ListSrv(user=user)
        lists = listsrv.find_list(str(datetime.datetime.now()), ListType.MOVIE)
        self.assertFalse(lists)

    def test_find_product_no_filter(self):
        products = ProductSrv().find_product("The Big")
        expected = Product(type=ProductType.MOVIE, title="The Big Lebowski", id="454350")
        self.assertIn(expected, products)

    def test_find_product_filtering(self):
        products = ProductSrv().find_product("The Big", ProductType.SERIE)
        unexpected = Product(type=ProductType.MOVIE, title="The Big Lebowski", id="454350")
        self.assertNotIn(unexpected, products)

