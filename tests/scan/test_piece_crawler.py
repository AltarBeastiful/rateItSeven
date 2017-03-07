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
from unittest.mock import patch

import guessit
from watchdog.events import FileSystemEvent

from rateItSeven.scan.piece import Piece
from rateItSeven.scan.piece_crawler import PieceCrawler
from tests.lib.test_case import RateItSevenTestCase


class TestPieceCrawler(RateItSevenTestCase):

    @patch("rateItSeven.scan.polling_observer_with_state.PollingObserverWithState")
    def test_should_add_new_piece_to_local_collection(self, mock_polling_observer_with_state):
        crawler = PieceCrawler(path="some/path")

        piece_1_path = "/etc/movie/jumanji-1995.mkv"
        piece_2_path = "/etc/movie/Dikkenek (2006).avi"

        crawler.on_created(FileSystemEvent(piece_1_path))
        crawler.on_created(FileSystemEvent(piece_2_path))

        self.assertEqual([
            Piece(path=piece_1_path, guess=guessit.guessit(piece_1_path)),
            Piece(path=piece_2_path, guess=guessit.guessit(piece_2_path)),
        ], crawler.local_collection().piece_list())

    def test_should_not_crawl_already_crawled_files(self):
        pass
