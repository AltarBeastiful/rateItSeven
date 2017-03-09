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

from rateItSeven.senscritique.domain.sc_list import ListType, ScList, ListItem
from rateItSeven.senscritique.sc_api import AuthentifiedService
from rateItSeven.senscritique.scrapper_mixin import ScrapperMixin


class ListService(AuthentifiedService, ScrapperMixin):
    _URL_ADD_LIST = "https://www.senscritique.com/lists/add.ajax"
    _URL_ADD_LIST_ITEM = "https://www.senscritique.com/items/add.ajax"
    _URL_SEARCH_LIST = "https://www.senscritique.com/sc2/%s/listes/all/%s/titre/page-%d.ajax"
    _URL_EDIT_LIST_ITEM = "https://www.senscritique.com/items/edit/%s.json"
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
            "subtype_id_related": list_type.value[0],
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
        list_item_id = self.parse_html(response).xpath(self.XPATH_LIST_ITEM_ID_AFTER_ADD)
        return list_item_id[0] if list_item_id else None


    def add_episode(self, sclist: ScList, product_id: str, description: str):
        """
        Add an episode to a list
        The serie will be added to the list if not done yet
        The given description will just be appended to the existing description otherwise
        :param sclist: The list where to add the episode
        :param product_id: the product id of the serie in which add the episode
        :param description: The description of the episode
        :return: the list item id of the serie inside this list
        """
        list_item = self.find_list_item(sclist=sclist, product_id=product_id)

        if list_item:
            url = self._URL_EDIT_LIST_ITEM % list_item.id
            self.send_post(url=url, data={"description": list_item.description + "\n" + description})
            return list_item.id

        else:
            return self.add_movie(sclist.compute_list_id(), product_id, description)

    def find_list_item(self, sclist: ScList, product_id: str):
        """
        Find a product in a list
        :param sclist: The list to search in
        :param product_id: The product id to search for
        :rtype: ListItem
        """
        response = self.send_get(url=self._BASE_URL_SENSCRITIQUE + sclist.path)

        xpath_item_container = '//li[@data-sc-product-id="%s"]' % product_id
        item_container = self.parse_html(response).xpath(xpath_item_container)

        if not item_container:
            return None

        [item_id] = item_container[0].xpath("@data-sc-item-id")
        item_descriptions = item_container[0].xpath('//div[@id="annotation-%s"]/text()' % item_id)

        return ListItem(id=item_id, list_id=sclist.compute_list_id(),
                        description="".join(item_descriptions))

    def find_list(self, title: str, list_type: ListType = ListType.MOVIE):
        """
        Look on SC for lists matching the given title in the given user lists
        :param title: the title of the list to find
        :param list_type: the type of list to find (Serie/Movie)
        :return: a list of ScList matching the title
        :rtype: generator(ScList)
        """
        page = 1
        list_paths = True
        while list_paths:
            url = self._build_list_search_url(page=page, list_type=list_type)
            response = self.send_post(url=url, data={"searchQuery": title})
            list_paths = self.parse_html(response).xpath("//a[@class='elth-thumbnail-title']")
            yield from [ScList(type=list_type, name=l.attrib["title"], path=l.attrib["href"]) for l in list_paths]
            page += 1

    def list_item_list(self, sc_list):
        """
        Returns all items of the ScList
        :type sc_list: ScList
        :rtype: list(ListItem)
        """
        page = 1

        while True:
            response = self.send_get(url=self._BASE_URL_SENSCRITIQUE + sc_list.page_url(index=page))
            html_content = html.fromstring(response.text)

            item_node_list = html_content.xpath('//li[@data-rel="list-item"]')

            if not item_node_list:
                raise StopIteration()

            for item_node in item_node_list:
                item_id = item_node.get('data-sc-product-id')

                # Find item description if any
                description = ""
                description_node_list = item_node.xpath("//div[contains(@id,'annotation')]")

                if description_node_list:
                    description = description_node_list[0].text

                # @todo parse product as well

                yield ListItem(id=item_id, description=description, list_id=sc_list.compute_list_id())

            page += 1

    def _build_list_search_url(self, page=1, list_type: ListType = None):
        lsttype = "all" if list_type is None else list_type.value[1]
        return str(self._URL_SEARCH_LIST % (self.user.username, lsttype, page))
