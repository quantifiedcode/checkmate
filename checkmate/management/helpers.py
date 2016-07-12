# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
import imp
import json
import yaml
import hashlib
import fnmatch

from collections import defaultdict

from blitzdb import SqlBackend
from sqlalchemy import create_engine

def get_project_path(path = None):
    if not path:
        path = os.getcwd()
    while path != "/":
        config_path = os.path.join(path,'.checkmate')
        if os.path.exists(config_path) and os.path.isdir(config_path):
            return path
        path = os.path.dirname(path)
    return None

def get_project_config(path):
    with open(os.path.join(path,".checkmate/config.json"),"r") as config_file:
        return json.loads(config_file.read())

def save_project_config(path,config):
    with open(os.path.join(path,".checkmate/config.json"),"w") as config_file:
        config_file.write(json.dumps(config))

def get_files_list(path,with_sha = False):
    files = []
    for (dirpath,dirnames,filenames) in os.walk(path):
        files.extend([(os.path.join(dirpath,f))[len(path):] for f in filenames])
    return files

def apply_filter(filename,patterns):
    return reduce(lambda x,y:x or y,[True if re.search(pattern,filename,re.UNICODE)
                                     else False for pattern in patterns],False)

def filter_filenames_by_analyzers(filenames,analyzers,language_patterns):
    filtered_filenames = []
    for filename in filenames:
        for analyzer_params in analyzers:
            if not analyzer_params['language'] in language_patterns:
                continue
            language_pattern = language_patterns[analyzer_params['language']]
            if not 'patterns' in language_pattern \
            or not apply_filter(filename,language_pattern['patterns']):
                continue
            filtered_filenames.append(filename)
            break
    return filtered_filenames

def filter_filenames_by_checkignore(file_paths,checkignore_patterns):

    filtered_file_paths = []

    for file_path in file_paths:
        excluded = False
        always_included = False
        for pattern in checkignore_patterns:
            if pattern.startswith("!"):
                if fnmatch.fnmatch(file_path,pattern[1:]):
                    always_included = True
                    break
            if fnmatch.fnmatch(file_path,pattern):
                excluded = True
        if not excluded or always_included:
            filtered_file_paths.append(file_path)
    return filtered_file_paths

def parse_checkmate_settings(content):
    """
    Basically a simple .yml parser that returns a simple Python dict to be used later on.
    """

    return yaml.load(content)

def parse_checkignore(content):

    lines = [l for l in [s.strip() for s in content.split("\n")] if l and not l[0] == '#']

    return lines

def get_project_and_backend(path, settings, echo = False,initialize_db = True):
    project_path = get_project_path(path)
    project_config = get_project_config(project_path)
    backend = get_backend(project_path,project_config,settings,echo = echo,initialize_db = initialize_db)
    project = get_project(project_path,project_config,settings,backend)
    return project,backend

def get_backend(project_path,project_config,settings,echo = False,initialize_db = True):
    backend_config = project_config['backend']
    engine = create_engine('sqlite:///%s' % os.path.join(project_path,'.checkmate/db.sqlite'),echo=echo)
    backend = SqlBackend(engine)

    if initialize_db:
        backend.create_schema()
        return backend

        #we run the Alembic migration script.
        print "Running migrations..."
        from checkmate.management.commands.alembic import Command as AlembicCommand
        alembic_command = AlembicCommand(None,backend,args = ['upgrade','head'])
        alembic_command.run()
        print "Done running migrations..."

    return backend

def get_project(project_path,project_config,settings,backend):
    project_class = project_config.get('project_class','Project')
    ProjectClass = settings.models[project_class]

    try:
        project = backend.get(ProjectClass,{'pk' : project_config['project_id']})
    except ProjectClass.DoesNotExist:
        project = ProjectClass({'pk' : project_config['project_id']})
        backend.save(project)
        #we retrieve the project from the DB, so that all the hooks get executed properly.
        project = backend.get(ProjectClass,{'pk' : project_config['project_id']})

    project.path = project_path

    settings.call_hooks('project.initialize', project)

    with backend.transaction():
        backend.save(project)

    return project
