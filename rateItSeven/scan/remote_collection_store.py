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
from contracts import contract, new_contract
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.scan.piece import Piece
from rateItSeven.senscritique.domain.sc_list import ListType
from rateItSeven.senscritique.list_service import ListService
from rateItSeven.senscritique.product_service import ProductService
from rateItSeven.senscritique.sc_api import AuthService

new_contract("Piece", Piece)


@synthesize_constructor()
@synthesize_property('email', contract='string')
@synthesize_property('password', contract='string')
@synthesize_property('movie_collection_title', contract='string', default="MyMovieList")
class RemoteCollectionStore(object):

    def __init__(self):
        self._user = AuthService().do_login(email=self.email, password=self.password)
        self._list_service = ListService(user=self._user)

        matching_list_list = self._list_service.find_list(self.movie_collection_title, list_type=ListType.MOVIE)

        if not matching_list_list:
            self._movie_list = self._list_service.create_list(name=self.movie_collection_title,
                                                              list_type=ListType.MOVIE)
        else:
            self._movie_list = matching_list_list[0]

    @contract
    def add(self, piece):
        """
        :param Piece piece:
        :rtype: bool
        """
        product_search_result = ProductService().find_product(piece.guess)

        if not product_search_result:
            return False

        item_id = ListService(self._user).add_movie(list_id=self._movie_list.compute_list_id(),
                                                    product_id=product_search_result[0].id)

        return item_id is not None
