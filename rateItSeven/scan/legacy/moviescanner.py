#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
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

import guessit
from rateItSeven.scan.legacy.filescanner import FileScanner

from rateItSeven.scan.legacy.containers.movieguess import MovieGuess


class MovieScanner(object):
    """
    Scan file system directories for video files
    Find info for each file wrapped into a MovieGuess
    """

    def __init__(self, dir_paths: list):
        self.dir_paths = dir_paths

    def list_movies(self):
        return self.list_videos_in_types(["movie"])

    def list_episodes(self):
        return self.list_videos_in_types(["episode"])

    def list_videos_in_types(self, video_types):
        file_scanner = FileScanner(self.dir_paths)
        for abs_path in file_scanner.absolute_file_paths():
            guess = MovieGuess(guessit.guessit(abs_path), abs_path)
            if guess.is_video_in_types(video_types):
                yield guess
