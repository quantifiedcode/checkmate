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

import os
import re
import imp
import json
import yaml
import hashlib
import fnmatch

from collections import defaultdict

def get_project_path(path = None):
    if not path:
        path = os.getcwd()
    while path != "/":
        files = os.listdir(path)
        if ".checkmate" in files and os.path.isdir(path+"/.checkmate"):
            return path
        path = os.path.dirname(path)
    return None

def get_project_config(path):
    with open(path+"/config.json","r") as config_file:
        return json.loads(config_file.read())

def save_project_config(path,config):
    with open(path+"/config.json","w") as config_file:
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
    """
    gitignore format:

    -A blank line matches no files, so it can serve as a separator for readability.
    -A line starting with # serves as a comment.
    -An optional prefix ! which negates the pattern; any matching file excluded by a previous pattern will become included again. If a negated pattern matches, this will override lower precedence patterns sources.
    -If the pattern ends with a slash, it is removed for the purpose of the following description, but it would only find a match with a directory. In other words, foo/ will match a directory foo and paths underneath it, but will not match a regular file or a symbolic link foo (this is consistent with the way how pathspec works in general in git).
    -If the pattern does not contain a slash /, git treats it as a shell glob pattern and checks for a match against the pathname relative to the location of the .gitignore file (relative to the toplevel of the work tree if not from a .gitignore file).
    -Otherwise, git treats the pattern as a shell glob suitable for consumption by fnmatch(3) with the FNM_PATHNAME flag: wildcards in the pattern will not match a / in the pathname. For example, "Documentation/*.html" matches "Documentation/git.html" but not "Documentation/ppc/ppc.html" or "tools/perf/Documentation/perf.html".
    -A leading slash matches the beginning of the pathname. For example, "/*.c" matches "cat-file.c" but not "mozilla-sha1/sha1.c".
    """

    lines = [l for l in [s.strip() for s in content.split("\n")] if l and not l[0] == '#']

    return lines