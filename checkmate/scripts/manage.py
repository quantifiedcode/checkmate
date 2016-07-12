#!/usr/bin/env python
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
import sys
import gzip
import time
import six
import os
import importlib
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

from types import ModuleType

import checkmate

from checkmate.management import helpers,commands
from checkmate.management.helpers import (get_project_path,
                                          get_project,
                                          get_backend,
                                          get_project_config)

from checkmate.settings import Settings

def load_command_class(settings):
    i = 1
    command_chain = []
    current_commands = settings.commands
    while True:
        if len(sys.argv) < i+1:
            sys.stderr.write("Usage: checkmate [command] [command] [...] [args]\n\nType \"checkmate help\" for help\n")
            exit(-1)
        cmd = sys.argv[i]
        command_chain.append(cmd)
        i+=1
        if not cmd in current_commands:
            sys.stderr.write("Unknown command: %s\n" % " ".join(command_chain))
            exit(-1)
        if not isinstance(current_commands[cmd],dict):
            if isinstance(current_commands[cmd],six.string_types):#it is a module/class string
                command_module_name,command_class_name = current_commands[cmd].rsplit(".",1)
                command_module = importlib.import_module(command_module_name)
                return getattr(command_module,command_class_name),command_chain
            else:#it is a class
                return current_commands[cmd],command_chain
        current_commands = current_commands[cmd]

def main():

    project_path = get_project_path()

    settings = Settings()
    settings.update(settings.load(project_path=project_path))
    settings.load_plugins()

    if project_path:
        project_config = get_project_config(project_path)
        backend = get_backend(project_path, project_config, settings)
        project = get_project(project_path, project_config, settings, backend)
    else:
        project = None
        backend = None

    CommandClass,command_chain = load_command_class(settings)

    if CommandClass.requires_valid_project and project is None:
        sys.stderr.write("Cannot find a checkmate project in the current directory tree, aborting.\n")
        exit(-1)

    command = CommandClass(project,settings,
                           backend=backend,
                           prog = sys.argv[0]+" "+" ".join(command_chain),
                           args = sys.argv[1+len(command_chain):])
    try:
        if 'help' in command.opts and command.opts['help']:
            print command.help_message()
            exit(0)
        result = command.run()
        if hasattr(command,'serialize'):
            result_str = command.serialize(result,'text')
            print result_str
    except KeyboardInterrupt:
        print "[CTRL-C pressed, aborting]"
        exit(-1)

if __name__ == '__main__':
    main()
