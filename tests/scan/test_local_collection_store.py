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
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from rateItSeven.scan.local_collection_store import LocalCollectionStore
from rateItSeven.scan.piece import Piece
from tests.lib.test_case import RateItSevenTestCase


class TestLocalCollectionStore(RateItSevenTestCase):

    def test_should_list_all_saved_piece(self):
        collection = LocalCollectionStore(path="")

        piece_1 = Piece(path="some/path/1")
        piece_2 = Piece(path="some/path/2")

        collection.add(piece=piece_1)
        collection.add(piece=piece_2)

        self.assertEqual([piece_1, piece_2], collection.piece_list())
