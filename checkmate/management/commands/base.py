# -*- coding: utf-8 -*-
"""
This file is part of checkmate, a meta code checker written in Python.

Copyright (C) 2015 Andreas Dewes, QuantifiedCode UG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import argparse
import copy

class CommandException(BaseException):
    pass

class BaseCommand(object):

    requires_valid_project = True
    options = [
        {
        'name'        : '--help',
        'action'      : 'store_true',
        'dest'        : 'help',
        'default'     : False,
        'help'        : 'display this help message.'
        },
        {
        'name'        : '--non-interactive',
        'action'      : 'store_true',
        'dest'        : 'non_interactive',
        'default'     : False,
        'help'        : 'non-interactive mode.'
        },
        ]

    description = None

    def __init__(self,project,backend = None,prog = None,args = None):
        self.project = project
        self.backend = backend
        self.prog = prog
        self.parse_args(args if args else [])

    def _get_parser(self):
        parser = argparse.ArgumentParser(self.prog,add_help = False,description = self.description)
        for opt in self.options:
            c_opt = copy.deepcopy(opt)
            name = c_opt['name']
            del c_opt['name']
            parser.add_argument(name,**c_opt)
        return parser

    def parse_args(self,raw_args):
        parser = self._get_parser()
        args,self.extra_args = parser.parse_known_args(raw_args)
        self.raw_args = raw_args
        self.opts = vars(args)

    def help_message(self):
        parser = self._get_parser()
        return parser.format_help()
        