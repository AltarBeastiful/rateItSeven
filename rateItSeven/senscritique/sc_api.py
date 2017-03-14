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
import json

import re
import requests
from abc import ABC
from contracts import contract, new_contract
from lxml import html
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.senscritique.domain.product import ProductType, Product
from rateItSeven.senscritique.domain.user import User


class ScRequester(ABC):
    _HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept-encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest'
    }
    _BASE_URL_SENSCRITIQUE = "https://www.senscritique.com"

    def send_get(self, url, params=None, **kwargs):
        return requests.get(url=url, headers=self._HEADERS, allow_redirects=False, params=params, **kwargs)

    def send_post(self, url, data=None, json_data=None, **kwargs):
        response = requests.post(url, data=data, json=json_data, headers=self._HEADERS, allow_redirects=False, **kwargs)
        if response.status_code >= 400:
            raise BadRequestException({
                "message": "Request didn't terminate correctly",
                "response": response
            })
        return response


@synthesize_property('user', contract=User)
@synthesize_constructor()
class AuthentifiedService(ScRequester):

    def __init__(self):
        pass

    def send_get(self, url, params=None, **kwargs):
        return ScRequester.send_get(self, url=url, params=params, cookies=self.user.session_cookies, **kwargs)

    def send_post(self, url, data=None, json_data=None, **kwargs):
        return ScRequester.send_post(self, url, data=data, json_data=json_data, cookies=self.user.session_cookies, **kwargs)


new_contract("User", User)


class AuthService(ScRequester):
    _URL = "https://www.senscritique.com/sc2/auth/login.json"
    _URL_HOME = "https://www.senscritique.com/live"

    def do_login(self, email, password):
        """
        Send a login request with the given credentials
        :return: The session cookies returned by SC
        :rtype: User
        """
        data = {
            'email': email,
            'pass': password,
        }
        response = self.send_post(self._URL, data=data)
        content = json.loads(response.text)
        if not content["json"]["success"]:
            raise UnauthorizedException
        username = self._find_username(cookies=response.cookies)
        return User(email=email, password=password, session_cookies=response.cookies, username=username)

    @contract
    def is_authenticated(self, user):
        """
        :type user: User
        :rtype: bool
        """

        if user.session_cookies is None or len(user.session_cookies) == 0:
            return False

        service = AuthentifiedService(user=user)
        response = service.send_get("https://www.senscritique.com/sc2/userActions/index.json")
        if response.status_code == 401:
            return False

        if response.status_code != 200:
            # @todo Fix laziness to setup proper logging
            print("Authenticated check got unexpected error: {status_code}"
                  .format(status_code=response.status_code))
            return False

        return True

    def _find_username(self, cookies):
        response = requests.get(url=self._URL_HOME, allow_redirects=False, cookies=cookies)
        [username] = html.fromstring(response.content).xpath("//span[@class='lahe-userMenu-username']/child::text()")
        return username


class UnauthorizedException(Exception):
    pass


class BadRequestException(Exception):
    pass
