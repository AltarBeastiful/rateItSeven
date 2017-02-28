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

import requests
from lxml import html
from rateItSeven.senscritique.domain.user import User
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.senscritique.domain.sc_list import ListType, ScList


class ScSrv(ABC):
    _HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept-encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest'
    }
    def send_post(self, url, data=None, json_data=None, **kwargs):
        response = requests.post(url, data=data, json=json_data, headers=self._HEADERS, allow_redirects=False, **kwargs)
        if response.status_code >= 400:
            raise BadRequestException({
                "message": "Request didn't terminate correctly",
                "response": response
            })
        return response


class AuthSrv(ScSrv):
    _URL = "https://www.senscritique.com/sc2/auth/login.json"
    _URL_HOME = "https://www.senscritique.com/live"

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
        response = self.send_post(self._URL, data=data)
        content = json.loads(response.text)
        if not content["json"]["success"]:
            raise UnauthorizedException
        username = self._find_username(cookies=response.cookies)
        return User(email=email, password=password, session_cookies=response.cookies, username=username)

    def _find_username(self, cookies):
        response = requests.get(url=self._URL_HOME, allow_redirects=False, cookies=cookies)
        [username] = html.fromstring(response.content).xpath("//span[@class='lahe-userMenu-username']/child::text()")
        return username


@synthesize_property('user', contract=User)
@synthesize_constructor()
class ListSrv(ScSrv):
    _URL_ADD_LIST = "https://www.senscritique.com/lists/add.ajax"
    _URL_ADD_LIST_ITEM = "https://www.senscritique.com/items/add.ajax"
    _URL_SEARCH_LIST = "https://www.senscritique.com/sc2/%s/listes/all/%s/titre/page-%d.ajax"
    _SUB_TYPE_ID = "22"
    XPATH_LIST_ITEM_ID_AFTER_ADD = '//li[@data-rel="sc-item-delete"]/@data-sc-item-id'

    def create_list(self, name: str, list_type: ListType):
        """
        Create an SC list
        :param name: The name of the list to create
        :param list_type: The type of list to create, eg Movie, Serie
        :return: the SC path to access the list, created by SC using the name and a random id
        :rtype: ScList
        """
        data = {
            "label": name,
            "subtype_id_related": "1",
            "is_ordered": 0,
            "is_public": 0
        }
        response = self.send_post(self._URL_ADD_LIST, data=data, cookies=self.user.session_cookies)
        return ScList(type=list_type, name=name, path=response.headers["Location"])

    def add_movie(self, list_id: str, product_id: str, description=""):
        """
        Add an item to a SC list
        :param list_id: the list id where to put the given movie/serie
        :param product_id: the SC id of the movie/serie to add
        :param description: A description for that item in the list
        :return: the SC list item id used to identify the new item in the list
        """
        data = {
            "list_id": list_id,
            "subtype_id": self._SUB_TYPE_ID,
            "product_id": product_id,
            "description": description
        }
        response = self.send_post(self._URL_ADD_LIST_ITEM,
                                 data=data,
                                 cookies=self.user.session_cookies)
        list_item_id = html.fromstring(response.content).xpath(self.XPATH_LIST_ITEM_ID_AFTER_ADD)
        return list_item_id[0] if list_item_id else None


    def _build_list_search_url(self, page=1, list_type : ListType = None):
        lsttype = "all" if list_type is None else list_type.value[1]
        return str(self._URL_SEARCH_LIST % (self.user.username, lsttype, page))


class UnauthorizedException(Exception):
    pass


class BadRequestException(Exception):
    pass
