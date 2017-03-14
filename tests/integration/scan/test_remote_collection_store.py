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
import uuid

from guessit import guessit

from rateItSeven.scan.piece import Piece
from rateItSeven.scan.remote_collection_store import RemoteCollectionStore
from rateItSeven.senscritique.list_service import ListService
from rateItSeven.senscritique.sc_api import AuthService
from tests.lib.test_case import RateItSevenTestCase


class TestRemoteCollectionStore(RateItSevenTestCase):

    def test_should_add_movies_to_sc_list(self):
        # GIVEN
        random_list_title = uuid.uuid4()

        user = AuthService().do_login(email="legalizme@gmail.com", password="12345")
        collection = RemoteCollectionStore(user=user, movie_collection_title=random_list_title.hex)

        path_1 = "/home/remi/Downloads/The Life Aquatic with Steve Zissou (2004) [1080p]/The.Life.Aquatic.with.Steve.Zissou.2004.1080p.BluRay.x264.YIFY.mp4"
        path_2 = "/home/remi/Downloads/files_to_scan/The Big Lebowski.mkv"

        # WHEN
        collection.add(piece=Piece(path=path_1, guess=guessit(path_1)))
        collection.add(piece=Piece(path=path_2, guess=guessit(path_2)))

        # THEN
        piece_list = list(collection.piece_list())
        self.assertEqual(2, len(piece_list))

        # @todo uncomment when product parsing is implement in ListService.list_item_list
        # self.assertEqual("The Big Lebowski", sc_list[0].product.title)
        # self.assertEqual("La Vie aquatique", sc_list[1].product.title)
