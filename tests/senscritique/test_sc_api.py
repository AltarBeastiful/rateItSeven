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

from requests.cookies import RequestsCookieJar

from rateItSeven.senscritique.domain.sc_list import ListType
from rateItSeven.senscritique.domain.user import User
from rateItSeven.senscritique.list_service import ListService
from rateItSeven.senscritique.sc_api import AuthService, UnauthorizedException
from tests.lib.test_case import RateItSevenTestCase


class TestScApi(RateItSevenTestCase):
    LIST_NODES_XPATH = '//div[@data-rel="lists-content"]/ul/li'

    def test_login_success(self):
        user = self.authentified_user()
        self.assertNotEqual(0, len(user.session_cookies))
        self.assertEqual("invite-san", user.username)

    def test_login_failure(self):
        with self.assertRaises(UnauthorizedException) as exc_catcher:
            response = AuthService().do_login(u"alogin", "badpassword")

    def test_authenticated_can_do_authenticated_request(self):
        user = self.authentified_user()

        self.assertTrue(AuthService().is_authenticated(user=user))

        list_generator = ListService(user=user).find_list("find_", ListType.MOVIE)
        self.assertCountGreater(list_generator, 0)

    def test_is_authenticated_false_if_session_cookies_none(self):
        user = User(email="", password="", username="", session_cookies=None)

        self.assertFalse(AuthService().is_authenticated(user=user))

    def test_is_authenticated_false_if_session_cookies_empty(self):
        user = User(email="", password="", username="", session_cookies=RequestsCookieJar())

        self.assertFalse(AuthService().is_authenticated(user=user))

    def test_is_authenticated_false_if_authenticated_request_fails(self):
        cookie_jar = RequestsCookieJar()
        cookie_jar.set('gross_cookie', 'yum', domain='senscritique.com')
        user = User(email="", password="", username="", session_cookies=cookie_jar)

        self.assertFalse(AuthService().is_authenticated(user=user))
