# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
import copy

class BaseCommand(object):

    class CommandException(BaseException):
        pass

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
        {
        'name'        : '--format',
        'action'      : 'store',
        'dest'        : 'format',
        'default'     : 'python',
        'help'        : 'the output format for the return value of the command.'
        },
        ]

    description = None

    def __init__(self, project, settings, backend=None, prog=None, args=None):
        self.project = project
        self.settings = settings
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
