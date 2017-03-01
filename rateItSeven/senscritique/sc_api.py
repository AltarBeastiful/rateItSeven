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
from abc import ABC

import requests
from lxml import html
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.senscritique.domain.product import ProductType, Product
from rateItSeven.senscritique.domain.sc_list import ListType, ScList
from rateItSeven.senscritique.domain.user import User


class ScRequester(ABC):
    _HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept-encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest'
    }

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

    def send_post(self, url, data=None, json_data=None, **kwargs):
        return ScRequester.send_post(self, url, data=data, json_data=json_data, cookies=self.user.session_cookies, **kwargs)


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

    def _find_username(self, cookies):
        response = requests.get(url=self._URL_HOME, allow_redirects=False, cookies=cookies)
        [username] = html.fromstring(response.content).xpath("//span[@class='lahe-userMenu-username']/child::text()")
        return username


class ListService(AuthentifiedService):
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
        response = self.send_post(self._URL_ADD_LIST, data=data)
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
        response = self.send_post(self._URL_ADD_LIST_ITEM, data=data)
        list_item_id = html.fromstring(response.content).xpath(self.XPATH_LIST_ITEM_ID_AFTER_ADD)
        return list_item_id[0] if list_item_id else None

    def find_list(self, title: str, list_type: ListType = ListType.MOVIE):
        """
        Look on SC for lists matching the given title in the given user lists
        :param title: the title of the list to find
        :param list_type: the type of list to find (Serie/Movie)
        :return: a list of ScList matching the title
        :rtype: list
        """
        page = 1
        list_paths = True
        lists = []
        while list_paths:
            url = self._build_list_search_url(page=page, list_type=list_type)
            response = self.send_post(url=url, data={"searchQuery": title})
            list_paths = html.fromstring(response.content).xpath("//a[@class='elth-thumbnail-title']")
            lists += [ScList(type=list_type, name=l.attrib["title"], path=l.attrib["href"]) for l in list_paths]
            page += 1
        return lists

    def _build_list_search_url(self, page=1, list_type: ListType = None):
        lsttype = "all" if list_type is None else list_type.value[1]
        return str(self._URL_SEARCH_LIST % (self.user.username, lsttype, page))


class ProductService(ScRequester):
    _URL_SEARCH = "https://www.senscritique.com/sc2/search/autocomplete.json"

    def find_product(self, title: str, product_type: ProductType = None) -> list:
        response = self.send_get(url=self._URL_SEARCH, params={"query": title})
        content = json.loads(response.text)
        products = [self._product_from_url(product["url"], product["originalLabel"]) for product in content["json"]]
        if product_type is not None:
            products = [product for product in products if product.type == product_type]
        return products

    def _product_from_url(self, url: str, title: str) -> Product:
        m = re.search(".*senscritique\.com/(.*)/.*/(.*)", url)
        return Product(type=ProductType(m.group(1)), title=title, id=m.group(2))


class UnauthorizedException(Exception):
    pass


class BadRequestException(Exception):
    pass
