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
from lxml import html

from rateItSeven.senscritique.domain.sc_list import ListType, ScList
from rateItSeven.senscritique.sc_api import AuthentifiedService


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

    def delete_list(self, list):
        """
        Delete a list
        :param ScList list:
        :rtype: bool
        """

        delete_url = "https://www.senscritique.com/sc2/lists/delete/%s.json" % (list.compute_list_id())

        response = self.send_post(delete_url, data={'confirm': True})
        return response.status_code == 200

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
        :rtype: generator
        """
        page = 1
        list_paths = True
        while list_paths:
            url = self._build_list_search_url(page=page, list_type=list_type)
            response = self.send_post(url=url, data={"searchQuery": title})
            list_paths = html.fromstring(response.content).xpath("//a[@class='elth-thumbnail-title']")
            yield from [ScList(type=list_type, name=l.attrib["title"], path=l.attrib["href"]) for l in list_paths]
            page += 1

    def _build_list_search_url(self, page=1, list_type: ListType = None):
        lsttype = "all" if list_type is None else list_type.value[1]
        return str(self._URL_SEARCH_LIST % (self.user.username, lsttype, page))
