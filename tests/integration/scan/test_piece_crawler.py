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
from unittest import skip

from watchdog.events import FileSystemEvent

from rateItSeven.scan.piece_crawler import PieceCrawler
from tests.lib.test_case import RateItSevenTestCase


class TestPieceCrawler(RateItSevenTestCase):

    def test_should_add_piece_to_remote_collection(self):
        random_remote_collection_title = uuid.uuid4().hex
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH, user=self.authentified_user(),
                               remote_collection_title=random_remote_collection_title)

        piece_1_path = "/etc/movie/jumanji-1995.mkv"
        piece_2_path = "/etc/movie/Dikkenek (2006).avi"

        crawler.on_created(FileSystemEvent(piece_1_path))
        crawler.on_created(FileSystemEvent(piece_2_path))

        self.assertCountGreater(crawler.remote_collection.piece_list(), 1)
