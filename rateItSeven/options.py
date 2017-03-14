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
Options
"""
import shlex
from argparse import ArgumentParser

from rateItSeven.conf.global_settings import APP_DATA_DIR


def build_argument_parser():
    """
    Builds the argument parser
    :return: the argument parser
    :rtype: ArgumentParser
    """
    opts = ArgumentParser()
    opts.add_argument(dest='paths', help='The path to your movie library folder (you can specify more than one)',
                      nargs='*')

    opts.add_argument('-u', '--username', dest='username', default=None,
                             help='Your SensCritique user name')

    opts.add_argument('-p', '--password', dest='password',
                             help='Your SensCritique password')

    opts.add_argument('-f', '--storefile', dest='store_file', default=APP_DATA_DIR + "/store",
                             help='Specify a specific store file previously created by another run of RateItSeven or '
                                  'a path to a nonexistant file that will be created by RateItSeven')

    opts.add_argument('-m', '--movielist', dest='movie_list', default='RateItSeven Films',
                             help='The name of the SensCritique list where to store your movie library')

    opts.add_argument('-s', '--serielist', dest='serie_list', default='RateItSeven Series',
                             help='The name of the SensCritique list where to store your serie library')

    opts.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                         help='Display debug output')

    opts.add_argument('--version', dest='version', action='store_true', default=False,
                                  help='Display the rateItSeven version.')

    return opts


def parse_options(options=None):
    """
    Parse given option string

    :param options:
    :type options:
    :return:
    :rtype:
    """
    if isinstance(options, str):
        args = shlex.split(options)
        options = vars(argument_parser.parse_args(args))
    elif options is None:
        options = vars(argument_parser.parse_args())
    elif not isinstance(options, dict):
        options = vars(argument_parser.parse_args(options))
    return options

argument_parser = build_argument_parser()

