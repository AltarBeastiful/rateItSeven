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
import unittest

from rateItSeven.senscritique.sc_api import AuthSrv, ListSrv, ListType


class TestLoginRequest(unittest.TestCase):
    LIST_NODES_XPATH = '//div[@data-rel="lists-content"]/ul/li'

    def setUp(self):
        self.login = "legalizme@gmail.com"
        self.password = "12345"

    def test_login_success(self):
        response = AuthSrv(self.login, self.password).dologin()
        self.assertNotEqual(0, len(response))

    def test_create_list(self):
        response = AuthSrv(self.login, self.password).dologin()
        listsrv = ListSrv(response)
        response = listsrv.create_list("myList_"+str(datetime.datetime.now()), ListType.MOVIE)
        self.assertIsNotNone(response)

