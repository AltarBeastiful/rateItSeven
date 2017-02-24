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
from abc import ABC
from enum import Enum

import requests
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.senscritique.domain.list import ListType, List
from rateItSeven.senscritique.domain.user import User

_HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept-encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest'
}


class ScSrv(ABC):
    def send_post(self, url, data=None, json_data=None, **kwargs):
        response = requests.post(url, data=data, json=json_data, allow_redirects=False, **kwargs)
        if response.status_code >= 400:
            raise BadRequestException({
                "message": "Request didn't terminate correctly",
                "response": response
            })
        return response


class AuthSrv(ScSrv):
    _URL = "https://www.senscritique.com/sc2/auth/login.json"

    def dologin(self, email, password):
        """
        Send a login request with the given credentials
        :return: The session cookies returned by SC
        :rtype: User
        """
        data = {
            'email': email,
            'pass': password,
        }
        response = self.send_post(self._URL, headers=_HEADERS, data=data)
        content = json.loads(response.text)
        if not content["json"]["success"]:
            raise UnauthorizedException
        return User(email=email, password=password, session_cookies=response.cookies)


@synthesize_property('user', contract=User)
@synthesize_constructor()
class ListSrv(ScSrv):
    _URL_ADD_LIST = "https://www.senscritique.com/lists/add.ajax"
    _URL_ADD_LIST_ITEM = "https://www.senscritique.com/items/add.ajax"
    _SUB_TYPE_ID = "22"
    XPATH_LIST_ITEM_ID_AFTER_ADD = '//li[@data-rel="sc-item-delete"]/@data-sc-item-id'

    def create_list(self, name: str, list_type: ListType):
        """
        Create an SC list
        :param name: The name of the list to create
        :param list_type: The type of list to create, eg Movie, Serie
        :return: the SC path to access the list, created by SC using the name and a random id
        """
        data = {
            "label": name,
            "subtype_id_related": "1",
            "is_ordered": 0,
            "is_public": 0
        }
        response = self.send_post(self._URL_ADD_LIST, headers=_HEADERS, data=data, cookies=self.user.session_cookies)
        return List(type=list_type, name=name, path=response.headers["Location"])


class UnauthorizedException(Exception):
    pass


class BadRequestException(Exception):
    pass
