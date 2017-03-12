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
import os

from os import listdir

from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from watchdog.utils.dirsnapshot import DirectorySnapshot

from rateItSeven.scan.local_collection_store import LocalCollectionStore
from rateItSeven.scan.piece import Piece
from rateItSeven.scan.polling_observer_with_state import WatchState, EmptyDirectorySnapshot
from tests.lib.test_case import RateItSevenTestCase


class TestLocalCollectionStore(RateItSevenTestCase):

    def test_should_list_all_saved_piece(self):
        collection = LocalCollectionStore(path="")

        piece_1 = Piece(path="some/path/1")
        piece_2 = Piece(path="some/path/2")

        collection.add(piece=piece_1)
        collection.add(piece=piece_2)

        self.assertEqual([piece_1, piece_2], collection.piece_list())

    def test_state_list_empty_first(self):
        collection = LocalCollectionStore(path="")

        self.assertEqual([], collection.state_list())

    def test_should_save_state_list(self):
        collection = LocalCollectionStore(path="")

        expected_state_list = [
            WatchState(path="/a/path/1", snapshot=EmptyDirectorySnapshot(path=self.FIXTURE_FILES_PATH)),
            WatchState(path="/a/path/2", snapshot=DirectorySnapshot(self.FIXTURE_FILES_PATH, True, stat=os.stat, listdir=listdir)),
        ]

        # WHEN
        collection.set_state_list(expected_state_list)

        # THEN
        saved_file_list = collection.state_list()

        self.assertEqual("/a/path/1", saved_file_list[0].path)
        self.assertEqual("/a/path/2", saved_file_list[1].path)

        self.assertEqualSnapshot(expected_state_list[0].snapshot, saved_file_list[0].snapshot)
        self.assertEqualSnapshot(expected_state_list[1].snapshot, saved_file_list[1].snapshot)
