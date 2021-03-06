#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
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
import logging
import os

from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.conf.global_settings import APP_DATA_DIR
from rateItSeven.legacy.legacysenscritique import LegacySensCritique
from rateItSeven.legacy.movie import Movie
from rateItSeven.scan.legacy.moviestore import MovieStore
from rateItSeven.senscritique.domain.product import ProductType
from rateItSeven.senscritique.domain.sc_list import ListType
from rateItSeven.senscritique.list_service import ListService
from rateItSeven.senscritique.product_service import ProductService
from rateItSeven.senscritique.sc_api import AuthService, BadRequestException


@synthesize_property('login', contract=str)
@synthesize_property('password', contract=str)
@synthesize_property('search_paths', contract=list)
@synthesize_property('store_file_path', contract=str)
@synthesize_property('movie_list_name', contract=str, default='RateItSeven Films')
@synthesize_property('serie_list_name', contract=str, default='RateItSeven Series')
@synthesize_property('legacy_mode', contract=bool, default=False)
@synthesize_constructor()
class RateItSeven(object):
    def __init__(self):
        self._lists = {}
        self.lists_conf = {ListType.MOVIE: self._movie_list_name,
                           ListType.SERIE: self._serie_list_name}

    def start(self):
        self.init()
        if self._legacy_mode:
            self._start_legacy()
        else:
            self._start()

    def init(self):
        # Create user data folder
        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)

    def _start_legacy(self):
        sc = LegacySensCritique(self.login, self.password)
        sc.sign_in()
        for video_type, title in self.lists_conf.items():
            current_list = sc.retrieveListByTitle(title)
            if not current_list.isValid():
                sc.createList(current_list)
            self._lists[video_type] = current_list

        with MovieStore(self._store_file_path, self._search_paths) as store:
            changes = store.pull_changes()

            for video_type in self.lists_conf.keys():
                for guess in changes[video_type].added:
                    sc.addMovie(Movie(guess.get("title"), guess.abs_path), self._lists[video_type])

            store.persist_scanned_changes()

    def _start(self):
        # Login to SensCritique and initialize web services
        user = AuthService().do_login(email=self.login, password=self.password)
        listsrv = ListService(user)
        productsrv = ProductService()

        # Find and create if needed a list for each supported media
        for video_type, title in self.lists_conf.items():
            found_lists = list(listsrv.find_list(title=title, list_type=video_type))
            current_list = found_lists[0] if found_lists else listsrv.create_list(name=title, list_type=video_type)
            self._lists[video_type] = current_list

        # Pull changes made in the movie store and sync them with the lists on SensCritique
        store = MovieStore(self._store_file_path, self._search_paths)
        changes = store.pull_changes()

        for video_type in self.lists_conf.keys():
            product_type = ProductType.MOVIE if video_type == ListType.MOVIE else ProductType.SERIE
            list_id = self._lists[video_type].compute_list_id()

            # Media added since last check
            for guess in changes[video_type].added:
                # Search for the product on SensCritique from his guessed title and type
                products = productsrv.find_product(title=guess.get("title"), product_type=product_type)

                if products:
                    # Take the first result found by SC as it's the more likely to be the one we are looking for
                    product = products[0]
                    try:
                        if video_type == ListType.MOVIE:
                            listsrv.add_movie(list_id=list_id, product_id=product.id, description=guess.abs_path)
                        else:
                            description = "S%02d, E%02d : %s" % (guess.get("season"),
                                                                 guess.get("episode"),
                                                                 guess.abs_path)
                            listsrv.add_episode(self._lists[video_type],
                                                product_id=product.id,
                                                description=description)

                        logging.info("Product '%s' added to list '%s'"
                                     % (product.title, self._lists[video_type].name))

                    except BadRequestException:
                        logging.error("error adding '%s' to list. Already in it ?" % product.title)

                else:
                    logging.error("error '%s' not found on SC (%s)" % (guess.get("title"), guess.abs_path))

        store.persist_scanned_changes()
