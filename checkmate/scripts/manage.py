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
import importlib
from blitzdb import FileBackend
try:
    from blitzdb import MongoBackend
except ImportError:
    pass

import logging

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

from types import ModuleType

import checkmate
try:
    import pymongo
    pymongo_support = True
except ImportError:
    pymongo_support = False
from checkmate.management import helpers,commands
from checkmate.management.helpers import get_project_path,get_project_config,save_project_config

import checkmate.settings as settings

#print "Checkmate copy:",checkmate.__file__

"""
checkmate [summary]                                   Show a summary of the current project status
checkmate init                                        Create a new project
checkmate log                                         Show the project log
checkmate info                                        Show some basic information about the project
checkmate analyze [git|file]                          Analyze the project
checkmate issues [issue type]                         Show issues for the given filename
checkmate stats [statistics type]                     Show statistics for the given filename or directory
checkmate analyzers                                   List the currently enabled analyzers
checkmate analyzers enable [analyzer name]            Disable the given analyzer
checkmate analyzers disable [analyzer name]           Enable the given analyzer
checkmate reset                                       Reset the project 
checkmate export [issues/stats] [...]                 Export data from the project
checkmate reanalyze [snapshot ID] [file revision]     Reanalyze the project
checkmate compare issues [file revision 1] [...]      Compare file or snapshot issues 
checkmate compare stats [file revision 1] [...]       Compare file or snapshot statistics
checkmate help                                        Display this help text
"""

"""
Command structure:

checkmate [command name] [plain arg] --flag_name=[flag value] [plain arg] ...

"""

"""
Structure of .checkmate directory

.checkmate/
          /settings.json
          /init.py
          /db
"""

def load_command_class():
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


def get_project_and_backend(path):
    try:
        project_config = get_project_config(path+"/.checkmate")
    except (IOError,):
        sys.stderr.write("No project configuration found!\n")
        exit(-1)

    backend_config = project_config['backend']
    project_class = project_config.get('project_class','DiskProject')
    if not project_class in settings.models:
        sys.stderr.write("Invalid project type: %s. Maybe the plugin is missing?" % project_class)
        exit(-1)
    ProjectClass = settings.models[project_class]
    if backend_config['driver'] == 'mongo':
        if not pymongo_support:
            sys.stderr.write("Encountered pymongo backend, but pymongo is not installed!")
            exit(-1)
        pymongo_db = pymongo.MongoClient()[backend_config['db']]
        backend = MongoBackend(pymongo_db,autoload_embedded = False,allow_documents_in_query = False)
    elif backend_config['driver'] == 'file':
        backend = FileBackend(path+"/.checkmate",autoload_embedded = False)
    else:
        sys.stdout.write("Unknown backend driver: %s" % backend_config['driver'])
    try:
        project = backend.get(ProjectClass,{'pk' : project_config['project_id']})
    except ProjectClass.DoesNotExist:
        project = ProjectClass({'pk' : project_config['project_id']})
        backend.save(project)
    project.path = path
    backend.save(project)
    backend.commit()
    return project,backend

def main():

    settings.load_plugins()

    CommandClass,command_chain = load_command_class()
    project_path = get_project_path()

    if project_path:
        project,backend = get_project_and_backend(project_path)
    else:
        if CommandClass.requires_valid_project:
            sys.stderr.write("Cannot find a checkmate project in the current directory tree, aborting.\n")
            exit(-1)
        project = None
        backend = None

    command = CommandClass(project,backend,
                           prog = sys.argv[0]+" "+" ".join(command_chain),
                           args = sys.argv[1+len(command_chain):])
    try:
        if 'help' in command.opts and command.opts['help']:
            print command.help_message()
            exit(0)
        command.run()
    except KeyboardInterrupt:
        print "[CTRL-C pressed, aborting]"
        exit(-1)
if __name__ == '__main__':
    main()
