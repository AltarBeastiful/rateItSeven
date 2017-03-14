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
from datetime import timedelta

import guessit
from contracts import new_contract, contract
from synthetic import synthesize_constructor
from synthetic import synthesize_property
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from rateItSeven.scan.local_collection_store import LocalCollectionStore
from rateItSeven.scan.piece import Piece
from rateItSeven.scan.polling_observer_with_state import PollingObserverWithState, EmptyDirectorySnapshot
from rateItSeven.scan.remote_collection_store import RemoteCollectionStore, NotAuthenticatedError
from rateItSeven.senscritique.domain.user import User

new_contract('FileSystemEvent', FileSystemEvent)
new_contract('LocalCollectionStore', LocalCollectionStore)
new_contract('PollingObserverWithState', PollingObserverWithState)
new_contract('RemoteCollectionStore', RemoteCollectionStore)
new_contract('User', User)


@synthesize_constructor()
@synthesize_property('path', contract='string')
@synthesize_property('local_collection_path', contract='string', default="movie_collection.json")
@synthesize_property('user', contract='User|None')
@synthesize_property('remote_collection_title', contract='string|None', default="My Collection")
class PieceCrawler(FileSystemEventHandler):
    """
    Crawls your files, find your gems (movie or tv show) and add them to
    your local and remote collection.
    """
    DEFAULT_CRAWL_TIMEOUT = timedelta(minutes=1).total_seconds()

    def __init__(self):
        self._local_collection = LocalCollectionStore(path=self.local_collection_path)

        # Get previous watch state from local collection
        state_by_path = self._state_by_path()
        initial_state = state_by_path.get(self.path) or EmptyDirectorySnapshot(path=self.path)

        self._observer = PollingObserverWithState(timeout=self.DEFAULT_CRAWL_TIMEOUT)
        self._observer.schedule(event_handler=self, path=self.path, recursive=True,
                                initial_state=initial_state)

        self._remote_collection = None
        if self.user is not None:
            try:
                self._remote_collection = RemoteCollectionStore(user=self.user, movie_collection_title=self.remote_collection_title)
            except NotAuthenticatedError:
                pass

    @contract
    def on_created(self, event):
        """
        :param FileSystemEvent event:
        :rtype: None
        """
        if event.is_directory:
            return

        piece = Piece(path=event.src_path, guess=guessit.guessit(event.src_path))
        if not piece.is_movie():
            return

        self.local_collection().add(piece)

        # @todo save state_list to local collection here? What about concurrency?
        self.local_collection().set_state_list(self._observer.state_list())

        # Add to remote collection
        self._add_to_remote_collection(piece=piece)

    @contract
    def local_collection(self):
        """
        :rtype: LocalCollectionStore
        """

        return self._local_collection

    @property
    @contract
    def remote_collection(self):
        """
        :rtype: RemoteCollectionStore|None
        """
        return self._remote_collection

    @contract
    def file_observer(self):
        """
        :rtype: PollingObserverWithState
        """
        return self._observer

    def _state_by_path(self):
        return {state.path: state.snapshot for state in self.local_collection().state_list()}

    def _add_to_remote_collection(self, piece):
        remote_collection = self.remote_collection
        if remote_collection is not None:
            remote_collection.add(piece=piece)
