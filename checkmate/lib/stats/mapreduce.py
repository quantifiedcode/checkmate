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
from collections import defaultdict
import abc

class MapReducer(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def map(self,items):
        return []

    @abc.abstractmethod
    def reduce(self,key,values):
        return []

    def filter(self,items):
        return items

    def mapreduce(self,items):
        map_results = [item for sublist in [self.map(item) 
                       for item in self.filter(items)] 
                       for item in sublist if item]
        grouped_results = defaultdict(lambda :[])
        for key,value in map_results:
            grouped_results[key].append(value)
        return dict([(key,self.reduce(key,values)) 
                     for key,values in grouped_results.items()])