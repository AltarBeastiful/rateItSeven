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
"""
Entry point module
"""
import logging
import sys

from rateItSeven.options import parse_options, argument_parser
from rateItSeven.__version__ import __version__
from rateItSeven.rateitseven import RateItSeven


def main(args=None):
    """
    Main function for entry point
    """
    if args is None:
        options = parse_options()
    else:
        options = parse_options(args)

    if options.get('verbose'):
        logging.basicConfig(stream=sys.stdout, format='%(message)s')
        logging.getLogger().setLevel(logging.DEBUG)

    help_required = True

    if options.get('version'):
        help_required = False
        print('+-------------------------------------------------------+')
        print('+                 RateItSeven ' + __version__ + (26 - len(__version__)) * ' ' + '+')
        print('+-------------------------------------------------------+')
        print('|      Please report any bug or feature request at      |')
        print('|  https://github.com/AltarBeastiful/rateItSeven/issues |')
        print('+-------------------------------------------------------+')

    if options.get('username') and options.get('paths'):
        help_required = False

        password = options.get('password')
        if not password:
            # TODO Prompt for password
            pass

        # TODO configure process with Serie and Movie list names (optional arguments)
        main_process = RateItSeven(login=options.get('username'),
                                   password=password,
                                   search_paths=options.get('paths'),
                                   store_file_path=options.get('store_file'))
        main_process.start()

    if help_required:
        argument_parser.print_help()


if __name__ == '__main__':
    main()
