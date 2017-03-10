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
from unittest.mock import patch

import guessit
from watchdog.events import FileSystemEvent

from rateItSeven.scan.piece import Piece
from rateItSeven.scan.piece_crawler import PieceCrawler
from rateItSeven.scan.polling_observer_with_state import EmptyDirectorySnapshot, PollingObserverWithState
from tests.lib.test_case import RateItSevenTestCase
from tests.lib.watchdog_helper import TestWatchdogObserver


class TestPieceCrawler(RateItSevenTestCase):

    @patch.object(PollingObserverWithState, 'schedule')
    @patch.object(PollingObserverWithState, '__init__', return_value=None)
    @patch.object(EmptyDirectorySnapshot, '__init__', return_value=None)
    def test_should_add_new_piece_to_local_collection(self, *mocks):
        crawler = PieceCrawler(path="some/path")

        piece_1_path = "/etc/movie/jumanji-1995.mkv"
        piece_2_path = "/etc/movie/Dikkenek (2006).avi"

        crawler.on_created(FileSystemEvent(piece_1_path))
        crawler.on_created(FileSystemEvent(piece_2_path))

        self.assertEqual([
            Piece(path=piece_1_path, guess=guessit.guessit(piece_1_path)),
            Piece(path=piece_2_path, guess=guessit.guessit(piece_2_path)),
        ], crawler.local_collection().piece_list())

    def test_crawler_should_discover_file_in_path(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        self.assertGreater(len(crawler.local_collection().piece_list()), 0)

    def test_crawler_should_only_consider_movie_files(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        collection_path_list = [piece.path for piece in crawler.local_collection().piece_list()]

        normal_file_path = os.path.join(self.FIXTURE_FILES_PATH, "fake")
        self.assertNotIn(normal_file_path, collection_path_list)

        episode_1_path = os.path.join(self.FIXTURE_FILES_PATH, "Archer Season 5  (1080p H265 Joy)", "Archer S05E01 White Elephant (1080p H265 Joy).mkv")
        self.assertNotIn(episode_1_path, collection_path_list)

        movie_1_path = os.path.join(self.FIXTURE_FILES_PATH, "The Big Lebowski.mkv")
        self.assertIn(movie_1_path, collection_path_list)

    def test_crawler_should_ignore_directories(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)
        subdir_directory_path = os.path.join(self.FIXTURE_FILES_PATH, "subdir")

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        self.assertNotIn(subdir_directory_path, [piece.path for piece in crawler.local_collection().piece_list()])

    def test_should_not_crawl_already_crawled_files(self):
        pass
