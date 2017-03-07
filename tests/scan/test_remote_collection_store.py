#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2017, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2017, Paolo de Vathaire <paolo.devathaire@gmail.com>
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
from unittest import mock
from unittest.mock import patch

from rateItSeven.scan.remote_collection_store import RemoteCollectionStore
from rateItSeven.senscritique.domain.product import Product, ProductType
from rateItSeven.senscritique.domain.sc_list import ScList, ListType
from rateItSeven.senscritique.domain.user import User
from rateItSeven.senscritique.list_service import ListService
from rateItSeven.senscritique.product_service import ProductService
from rateItSeven.senscritique.sc_api import AuthService
from tests.fixture.fixture_list import FixtureList
from tests.lib.test_case import RateItSevenTestCase


class TestRemoteCollectionStore(RateItSevenTestCase):

    @patch.object(ListService, 'find_list', return_value=[ScList(name="a List", path="/liste/aList/aListId", type=ListType.MOVIE)])
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_should_add_piece_to_sc_list(self, mock_do_login, mock_add_movie, mock_find_product, *mocks):
        # GIVEN
        mock_do_login.return_value = User(email="meme@me.com", password="1234", username="meme")
        mock_find_product.return_value = [
            Product(title="SomeTitle", id="12345", type=ProductType.MOVIE),
        ]

        remote = RemoteCollectionStore(email="meme@me.com", password="1234")

        piece_1 = FixtureList.piece_list[0]
        piece_2 = FixtureList.piece_list[1]

        # WHEN
        self.assertTrue(remote.add(piece_1))
        self.assertTrue(remote.add(piece_2))

        # THEN
        self.assertTrue(mock_do_login.called)
        self.assertEqual(2, mock_add_movie.call_count)

    @patch.object(ListService, 'find_list', return_value=[ScList(name="a List", path="/liste/aList/aListId", type=ListType.MOVIE)])
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_add_takes_first_matching_sc_product(self, mock_do_login, mock_add_movie, mock_find_product, *mocks):
        mock_do_login.return_value = User(email="meme@me.com", password="1234", username="meme")
        mock_find_product.return_value = [
            Product(title="SomeTitle", id="12345", type=ProductType.MOVIE),
            Product(title="SomeTitle2", id="67890", type=ProductType.MOVIE),
        ]

        remote = RemoteCollectionStore(email="meme@me.com", password="1234")

        piece = FixtureList.piece_list[0]

        # WHEN
        remote.add(piece)

        # THEN
        mock_add_movie.assert_called_once_with(list_id=mock.ANY, product_id="12345")

    @patch.object(ListService, 'find_list', return_value=[ScList(name="a List", path="/liste/aList/aListId", type=ListType.MOVIE)])
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_add_cannot_find_piece_in_sc(self, mock_do_login, mock_add_movie, mock_find_product, *mocks):
        mock_do_login.return_value = User(email="meme@me.com", password="1234", username="meme")
        mock_find_product.return_value = [
        ]

        remote = RemoteCollectionStore(email="meme@me.com", password="1234")
        piece = FixtureList.piece_list[0]

        # WHEN
        result = remote.add(piece)

        # THEN
        self.assertFalse(result)
        self.assertFalse(mock_add_movie.called)

    @patch.object(ListService, 'find_list', return_value=[ScList(name="a List", path="/liste/aList/aListId", type=ListType.MOVIE)])
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_add_fail_to_add_piece_to_sc(self, mock_do_login, mock_add_movie, mock_find_product, *mocks):
        mock_do_login.return_value = User(email="meme@me.com", password="1234", username="meme")
        mock_find_product.return_value = [
            Product(title="SomeTitle", id="12345", type=ProductType.MOVIE),
        ]

        mock_add_movie.return_value = None

        remote = RemoteCollectionStore(email="meme@me.com", password="1234")
        piece = FixtureList.piece_list[0]

        # WHEN
        result = remote.add(piece)

        # THEN
        self.assertFalse(result)
        self.assertTrue(mock_add_movie.called)

    def test_add_should_give_a_nice_description_to_piece(self):
        pass

    @patch.object(ListService, 'find_list')
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_remote_collection_adds_to_specified_list(self, mock_do_login, mock_add_movie, mock_find_product, mock_find_list):
        mock_do_login.return_value = User(email="meme@me.com", password="1234", username="meme")
        mock_find_product.return_value = [
            Product(title="SomeTitle", id="12345", type=ProductType.MOVIE),
        ]
        mock_find_list.return_value = [
            ScList(name="a List", path="/liste/aList/aListId", type=ListType.MOVIE)
        ]

        piece = FixtureList.piece_list[0]

        # WHEN
        remote = RemoteCollectionStore(email="meme@me.com", password="1234")
        result = remote.add(piece)

        # THEN
        self.assertTrue(result)
        self.assertTrue(mock_find_list.called)
        mock_add_movie.assert_called_once_with(list_id="aListId", product_id="12345")

    @patch.object(ListService, 'find_list', return_value=[])
    @patch.object(ListService, 'create_list')
    @patch.object(ProductService, 'find_product')
    @patch.object(ListService, 'add_movie')
    @patch.object(AuthService, 'do_login')
    def test_remote_collection_creates_list_if_not_present(self, mock_do_login, mock_add_movie, mock_find_product, *mocks):
        #@todo implement
        pass
