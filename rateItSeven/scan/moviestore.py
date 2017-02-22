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

import json
import os

from rateItSeven.scan.moviescanner import MovieScanner
from rateItSeven.scan.containers.moviestorestate import MovieStoreState
from rateItSeven.scan.containers.movieguess import MovieGuess


class MovieStore(object):
    """
    Store movies metadata in file
    """
    _SUPPORTED_VIDEO_TYPES = ["movie", "episode"]

    def __init__(self, store_file_path: str, movies_dirs: list):
        self.store_file_path = store_file_path
        self.store_file = open(store_file_path, 'w')
        self.scanner = MovieScanner(movies_dirs)

    def __enter__(self):
        return self

    def __exit__(self, thetype, value, traceback):
        self.store_file.close()

    def persist_scanned_changes(self):
        """
        Persist all movies found at movies_dirs to the store file
        """
        scanned_movies = list(self.scanner.list_videos_in_types(MovieStore._SUPPORTED_VIDEO_TYPES))
        # Overwrite existing content
        self.store_file.seek(0)
        self.store_file.write(json.dumps(scanned_movies, default=lambda o: o.__dict__))
        self.store_file.flush()

    def pull_changes(self):
        """
        Compute a diff between the movies found at movies_dirs and the movies already in the store
        """
        scanned_movies = set(self.scanner.list_movies())
        scanned_episodes = set(self.scanner.list_episodes())

        # load stored movies if file contains data
        known_movies = set()
        known_episodes = set()
        if os.stat(self.store_file.name).st_size > 0:
            with open(self.store_file_path) as store_read:
                storestr = store_read.read()
            dict_guesses = json.loads(storestr)
            # create a set from loaded dict in order to compare with the set of scanned movies
            for movie in dict_guesses:
                guess = MovieGuess(movie["guess"], movie["abs_path"])
                if guess.is_movie():
                    known_movies.add(guess)
                elif guess.is_episode():
                    known_episodes.add(guess)

        return {"movies": self._create_store_state(scanned_movies, known_movies),
                "episodes": self._create_store_state(scanned_episodes, known_episodes)}

    @staticmethod
    def _create_store_state(scanned_videos, known_videos):
        # Compute diffs between stored videos and scanned videos
        added_videos = scanned_videos - known_videos
        existing_videos = set(scanned_videos & known_videos)
        deleted_videos = known_videos - scanned_videos

        return MovieStoreState(added_videos, existing_videos, deleted_videos)
