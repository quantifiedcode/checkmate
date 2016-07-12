# -*- coding: utf-8 -*-

from __future__ import unicode_literals

def directory_splitter(path,include_filename = False):
    if include_filename:
        path_hierarchy = path.split("/")
    else:
        path_hierarchy = path.split("/")[:-1]
    if path.startswith('/'):
        path_hierarchy = path_hierarchy[1:]
    paths = []
    current_path = ''
    for partial_path in path_hierarchy:
        paths.append(current_path)
        if current_path != '':
            current_path+='/'
        current_path+=partial_path
    paths.append(current_path)
    return paths
