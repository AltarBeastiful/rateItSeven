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

from lxml.html import HtmlElement

from rateItSeven.senscritique.domain.sc_list import ListType, ScList, ListItem
from rateItSeven.senscritique.product_service import product_from_url
from rateItSeven.senscritique.sc_api import AuthentifiedService
from rateItSeven.senscritique.scrapper_mixin import ScrapperMixin


def _build_list_item(item_node, list_id):
    """
    Build a ListItem from the corresponding HTML item node
    :param item_node: the HTML item node
    :type item_node: HtmlElement
    :param list_id: the id of the list in which the item belong
    :type list_id: str
    :return: the ListItem
    :rtype: ListItem
    """
    product_id = item_node.get('data-sc-product-id')
    item_id = item_node.get('data-sc-item-id')

    # Find item description if any
    item_description = "".join(item_node.xpath('//div[@id="annotation-%s"]/text()' % item_id))

    # Parse product info
    product_a = item_node.xpath("//a[@id='product-title-%s']" % product_id)
    product = product_from_url(product_a[0].attrib['href'], product_a[0].text) if product_a else None

    return ListItem(id=item_id, description=item_description, list_id=list_id, product=product)


class ListService(AuthentifiedService, ScrapperMixin):
    """
    A stateless service providing all list related operations on www.senscritique.com
    """
    _URL_ADD_LIST = "https://www.senscritique.com/lists/add.ajax"
    _URL_ADD_LIST_ITEM = "https://www.senscritique.com/items/add.ajax"
    _URL_REMOVE_LIST_ITEM = "https://www.senscritique.com/items/remove.json"
    _URL_SEARCH_LIST = "https://www.senscritique.com/sc2/%s/listes/all/%s/titre/page-%d.ajax"
    _URL_EDIT_LIST_ITEM = "https://www.senscritique.com/items/edit/%s.json"
    _SUB_TYPE_ID = "22"
    XPATH_LIST_ITEM_ID_AFTER_ADD = '//li[@data-rel="sc-item-delete"]/@data-sc-item-id'

    def create_list(self, name, list_type):
        """
        Create an SC list
        :param name: The name of the list to create
        :type name: str
        :param list_type: The type of list to create, eg Movie, Serie
        :type list_type: ListType
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

    def delete_list(self, list_to_delete):
        """
        Delete a list
        :param list_to_delete: the list to delete
        :type list_to_delete: ScList
        :return: True if list was successfully deleted, False otherwise
        :rtype: bool
        """
        delete_url = "https://www.senscritique.com/sc2/lists/delete/%s.json" % (list_to_delete.compute_list_id())
        response = self.send_post(delete_url, data={'confirm': True})

        return response.status_code == 200

    def add_movie(self, list_id, product_id, description=""):
        """
        Add an item to a SC list
        :param list_id: the list id where to put the given movie/serie
        :type list_id: str
        :param product_id: the SC id of the movie/serie to add
        :type product_id: str
        :param description: A description for that item in the list
        :type description: str
        :return: the SC list item id used to identify the new item in the list
        :rtype: str
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

    def remove_movie(self, list_id, item_id):
        """
        Remove an item from a SC list
        :param list_id: the list id from which to remove the movie/serie
        :type list_id: str
        :param item_id: the list item id of the item to remove
        :type item_id: str
        :return: True if delete operation succeeded, False otherwise
        :rtype: bool
        """
        data = {
            "listId": list_id,
            "itemId": item_id,
            "subtypeId": self._SUB_TYPE_ID
        }

        response = self.send_post(self._URL_REMOVE_LIST_ITEM, data=data)
        json_response = json.loads(response.text)

        return json_response["json"]["success"]

    def update_movie(self, item_id, description):
        """
        Change the description of the given list item
        :param item_id: the id of the item to update
        :type item_id: str
        :param description: the description to set
        :type description: str
        :return: True if operation suceeded, False otherwise
        :rtype: bool
        """
        url = self._URL_EDIT_LIST_ITEM % item_id
        response = self.send_post(url=url, data={"description": description})
        json_response = json.loads(response.text)
        return json_response["json"]["success"]

    def add_episode(self, sclist, product_id, description):
        """
        Add an episode to a list
        The serie will be added to the list if not done yet
        The given description will just be inserted in the existing description otherwise
        Episodes descriptions are sorted alphabetically in the serie
        :param sclist: The list where to add the episode
        :type sclist: ScList
        :param product_id: the product id of the serie in which add the episode
        :type product_id: str
        :param description: The description of the episode
        :type description: str
        :return: the list item id of the serie inside this list
        """
        list_item = self.find_list_item(sclist=sclist, product_id=product_id)

        if list_item:
            # Insert given descr on the right position by sorting lines alphabetically
            descr_list = list_item.description.split('\n')
            descr_list.append(description)
            descr_list.sort()

            url = self._URL_EDIT_LIST_ITEM % list_item.id
            self.send_post(url=url, data={"description": '\n'.join(descr_list)})
            return list_item.id

        else:
            return self.add_movie(sclist.compute_list_id(), product_id, description)

    def remove_episode(self, sclist, product_id, description):
        """
        Remove an episode from a serie in the given list
        :param sclist: the list that stores the serie
        :type sclist: ScList
        :param product_id: the product id of the serie
        :type product_id: str
        :param description: The description of the episode
        :type description: str
        :return: True if the episode was correctly removed, False otherwise
        :rtype: bool
        :raise ProductNotFoundException: if the product_id can't be found in the sclist
        """
        return self.update_episode(sclist=sclist,
                                   product_id=product_id,
                                   old_description=description,
                                   new_description='')

    def update_episode(self, sclist, product_id, old_description, new_description):
        """
        Remove an episode from a serie in the given list
        :param sclist: the list that stores the serie
        :type sclist: ScList
        :param product_id: the product id of the serie
        :type product_id: str
        :param old_description: The old description of the episode
        :type old_description: str
        :param new_description: The new description of the episode
        :type new_description: str
        :return: True if the episode was correctly updated, False otherwise
        :rtype: bool
        :raise ProductNotFoundException: if the product_id can't be found in the sclist
        """
        list_item = self.find_list_item(sclist=sclist, product_id=product_id)

        if list_item:
            descr_result = list_item.description.replace(old_description, new_description)
            if not new_description:
                descr_result = descr_result.replace('\n\n', '\n')

            url = self._URL_EDIT_LIST_ITEM % list_item.id
            response = self.send_post(url=url, data={"description": descr_result})

            json_response = json.loads(response.text)
            return json_response["json"]["success"]

        raise ProductNotFoundException()

    def find_list_item(self, sclist, product_id):
        """
        Find a product in a list
        :param sclist: The list to search in
        :type sclist: ScList
        :param product_id: The product id to search for
        :type product_id: str
        :return: The list item matching the given product id in the given list or None if not found
        :rtype: ListItem
        """
        list_id = sclist.compute_list_id()

        for page in self._list_pages(sclist):
            item_container = page.xpath('//li[@data-sc-product-id="%s"]' % product_id)

            if item_container:
                return _build_list_item(item_container[0], list_id)

        # Product not found
        return None

    def find_list(self, title, list_type=ListType.MOVIE):
        """
        Look on SC for lists matching the given title in the given user lists
        :param title: the title of the list to find
        :type title: str
        :param list_type: the type of list to find (Serie/Movie)
        :type list_type: ListType
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
        :param sc_list: the ScList
        :type sc_list: ScList
        :rtype: generator(ListItem)
        """
        list_id = sc_list.compute_list_id()

        for page in self._list_pages(sc_list):
            item_node_list = page.xpath('//li[@data-rel="list-item"]')
            for item_node in item_node_list:
                yield _build_list_item(item_node, list_id)

    def _list_pages(self, sc_list):
        i = 1

        while True:
            response = self.send_get(url=self._BASE_URL_SENSCRITIQUE + sc_list.page_url(index=i))
            html_content = self.parse_html(response)
            page = html_content.xpath('//ul[@data-sc-content-ul="true" and @data-rel="sortable"]')

            if not page or not page[0].xpath('//li[@data-rel="list-item"]'):
                raise StopIteration()

            yield page[0]

            i += 1

    def _build_list_search_url(self, page=1, list_type: ListType = None):
        lsttype = "all" if list_type is None else list_type.value[1]
        return str(self._URL_SEARCH_LIST % (self.user.username, lsttype, page))


class ProductNotFoundException(Exception):
    pass
