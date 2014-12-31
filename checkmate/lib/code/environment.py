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
import re
import time
import traceback
import logging
import six
import copy

from checkmate.management.helpers import (filter_filenames_by_analyzers,
                                          filter_filenames_by_checkignore)
from checkmate.settings import (language_patterns,
                                analyzers as all_analyzers,
                                aggregators as all_aggregators)

from checkmate.lib.stats.mapreduce import MapReducer
from checkmate.lib.analysis.base import BaseAnalyzer

from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalysisTimeAnalyzer(BaseAnalyzer):

    def summarize(self,items):

        stats = defaultdict(lambda : 0.0)

        for item in items:
            for analyzer,duration in item.items():
                stats[analyzer]+=duration

        return dict(stats)

def update_settings(all_analyzers,settings,type_name = "analyzers"):
    disabled_by_default = False
    if '%s_disabled_by_default' % type_name in settings:
        disabled_by_default = True

    if type_name in settings:
        analyzers = {}
        for name,params in all_analyzers.items():
            analyzers[name] = copy.copy(params)
            if not 'kwargs' in analyzers[name]:
                analyzers[name]['kwargs'] = {}
            if name in settings[type_name]:
                analyzer_settings = settings[type_name][name] 
                if analyzer_settings.get('disabled',False):
                    del analyzers[name]
                    continue
                analyzers[name]['kwargs'].update(analyzer_settings)
            elif disabled_by_default:
                del analyzers[name]
        return analyzers
    else:
        if disabled_by_default:
            return {}
        return all_analyzers

class CodeEnvironment(object):

    """
    Represents the full code environment of the project, including all code files.

    Responsibilities of the code environment:

    -Manage a list of all file revisions in the current project
    -Manage a list of all analyzers and aggregators to use
    -Manage project parameters that passed on to the analyzers
    """ 

    def __init__(self,
                 file_revisions,
                 analyzers = None,
                 aggregators = None,
                 raise_on_analysis_error = False,
                 settings = None,
                 env = None,
                 ):
        self._file_revisions = file_revisions
        self.raise_on_analysis_error = raise_on_analysis_error
        self._all_analyzers = analyzers if analyzers is not None else all_analyzers
        self._all_aggregators = aggregators if aggregators is not None else all_aggregators
        self._aggregators = None
        self._analyzers = None
        self._env = env if env is not None else {}
        self._settings = settings if settings is not None else {}
        self._analyzer_cache = {}

    @property
    def env(self):
        return self._env

    @property
    def analyzers(self):
        if self._analyzers is None:
            self._analyzers = update_settings(self._all_analyzers,self.settings,"analyzers")
        return self._analyzers

    @property
    def aggregators(self):
        if self._aggregators is None:
            self._aggregators = update_settings(self._all_aggregators,self.settings,"aggregators")
        return self._aggregators

    @property
    def file_revisions(self):
        return self._file_revisions

    @property
    def settings(self):
        return self._settings

    def get_language(self,file_revision):
        for language,language_pattern in language_patterns.items():
            if 'patterns' in language_pattern and \
                apply_filter(file_revision['path'],language_pattern['patterns']):
                return language
        return None

    def filter_file_revisions(self,file_revisions):
        analyzer_filter = lambda filenames : filter_filenames_by_analyzers(filenames,
                                                                           self.analyzers.values(),
                                                                           language_patterns)
        file_revisions_by_path = {fr.path : fr for fr in file_revisions}
        filtered_paths = {path : True for path in analyzer_filter(file_revisions_by_path.keys())}
        return [fr for path,fr in file_revisions_by_path.items() if path in 
                filtered_paths]


    def init_analyzer(self,name,parameters):
        class_str = parameters['class']
        
        if class_str in self._analyzer_cache:
            return self._analyzer_cache[class_str]

        kwargs = parameters['opts'] if 'opts' in parameters else {}

        #If we have settings for this analyzer, we add them to the keyword arguments
        if 'analyzers' in self.settings and name in self.settings['analyzers']:
            kwargs.update(self.settings['analyzers'][name])
        if isinstance(class_str,six.string_types):
            (module_name,separator,class_name) = class_str.rpartition(u".")
            module = __import__(module_name,globals(),locals(),[str(class_name)],-1)
            analyzer_class = getattr(module,class_name)
        else:
            analyzer_class = class_str
        analyzer = analyzer_class(self,**kwargs)
        self._analyzer_cache[class_str] = analyzer
        return analyzer

    def diff_summaries(self,snapshot_a,snapshot_b):

        summary = {}

        if not hasattr(snapshot_a,'summary') or not hasattr(snapshot_b,'summary'):
            return summary

        languages = set(snapshot_a.summary.keys()+snapshot_b.summary.keys())

        for language in languages:

            summary[language] = {}

            if not language in snapshot_a.summary or not language in snapshot_b.summary:
                continue

            language_summary_a = snapshot_a.summary[language]
            language_summary_b = snapshot_b.summary[language]

            for analyzer_name,analyzer_params in self.analyzers.items():

                if not analyzer_name in language_summary_a \
                   or not analyzer_name in language_summary_b:
                    continue

                summary[language][analyzer_name] = {}

                analyzer = self.init_analyzer(analyzer_name,analyzer_params)

                for key in language_summary_a[analyzer_name]:
                    if not key in language_summary_b[analyzer_name]:
                        continue
                    result = analyzer.diff_summary(language_summary_a[analyzer_name][key],
                                                   language_summary_b[analyzer_name][key]
                                                  )
                    if result:
                        summary[language][analyzer_name][key] = result

        return summary

    def summarize_issues(self,
                         issues,
                         significance_limit = 0.01,
                         group_by = ['language','analyzer','code']):

        """
        Summarizes a list of issues using a set of aggregators (usually directory-based)

        This function could be moved to a helper class since it does not make use of 
        environment-specific functionality (aside from the list of aggregators)
        """

        aggregators = self.aggregators.values()

        class IssuesMapReducer(MapReducer):

            def map(self,item):
                if 'file_revision' in item and 'language' in item['file_revision']:
                    item['language'] = item['file_revision']['language']
                for group in group_by:
                    if not group in item:
                        return []
                return [(key,item) for aggregator in aggregators 
                        for key in aggregator['mapper'](item['file_revision'])]

            def reduce(self,key,items):
                grouped_issues ={}

                if group_by:
                    for item in items:
                        invalid_item = False
                        current_dict = grouped_issues
                        for group in group_by[:-1]:
                            if not group in item:
                                invalid_item = True
                                break
                            if not item[group] in current_dict:
                                current_dict[item[group]] = {}
                            current_dict = current_dict[item[group]]
                        if not group_by[-1] in item:
                            invalid_item = True
                        if invalid_item:
                            continue
                        if not item[group_by[-1]] in current_dict:
                            current_dict[item[group_by[-1]]]= 0
                        current_dict[item[group_by[-1]]]+=1
                    return grouped_issues
                else:
                    issues_sum = 0
                    for item in items:
                        issues_sum+=1
                    return issues_sum


        map_reducer = IssuesMapReducer()

        return map_reducer.mapreduce(issues)

    def summarize(self,
                  file_revisions,
                  significance_limit = 0.01,
                  include_analysis_time = True):

        if not file_revisions:
            return {}

        results = defaultdict(lambda : defaultdict(lambda: defaultdict(dict)))
        file_revisions_by_key = defaultdict(lambda : {})

        for aggregator in self.aggregators.values():
            for file_revision in file_revisions:
                keys = aggregator['mapper'](file_revision)
                for key in keys:
                    if not file_revision['path'] in file_revisions_by_key[key]:
                        file_revisions_by_key[key][file_revision['path']] = file_revision

        for language in set([analyzer['language'] for analyzer in self.analyzers.values()]):
            for analyzer_name,analyzer_params in {name : analyzer 
                    for name, analyzer in self.analyzers.items()
                    if analyzer['language'] == language}.items():
                try:
                    analyzer = self.init_analyzer(analyzer_name,analyzer_params)
                    for key in file_revisions_by_key:
                        if hasattr(analyzer,'summarize_all'):
                            #If the analyzer has a `summarize_all` function we call it with the 
                            #results from ALL analyzers and its own name.
                            results[language][analyzer_name][key] = analyzer\
                                                                    .summarize_all([f['results'] 
                                for f in file_revisions_by_key[key].values() 
                                if 'results' in f and f['language'] == language]
                                ,analyzer_name)
                        else:
                            results[language][analyzer_name][key] = analyzer.summarize([
                                f['results'][analyzer_name] 
                                for f in file_revisions_by_key[key].values() 
                                if 'results' in f and f['language'] == language 
                                and analyzer_name in f['results']])
                except Exception as e:
                    logger.error("Could not summarize results for analyzers %s and key %s" % 
                        (analyzer_name,key))
                    raise
                    continue

            results[language] = dict(results[language])

        results = dict(results)
        return results

    def analyze_file_revisions(self,file_revisions):

        filtered_file_revisions =  self.filter_file_revisions(file_revisions)

        for file_revision in filtered_file_revisions:
            logger.info("Analyzing: "+file_revision['path'])
            file_revision.language = self.get_language(file_revision)
            file_revision.results = self.analyze_file_revision(file_revision,
                {analyzer_name : analyzer_params 
                    for analyzer_name,analyzer_params in self.analyzers.items()
                    if analyzer_params['language'] == file_revision.language})

        return filtered_file_revisions

    def analyze_file_revision(self,file_revision,analyzers):

        analysis_time = {}
        results = {}

        for analyzer_name,analyzer_params in analyzers.items():
            try:
                analyzer = self.init_analyzer(analyzer_name,analyzer_params)
                
                start = time.time()
                analyzer_results = analyzer.analyze(file_revision)
                stop = time.time()
                
                analysis_time[analyzer_name] = stop-start

                if analyzer_results:
                    results[analyzer_name] = analyzer_results
                else:
                    results[analyzer_name] = {}

            except Exception as e:
                if self.raise_on_analysis_error:
                    raise
                logger.error("Error when running analyzer %s on file %s:" % 
                             (analyzer_name,file_revision.path))
                logger.error(traceback.format_exc())
                issue = {
                    'code' : 'AnalysisError',
                    'analyzer' : analyzer_name,
                    'data' : {
                        'exception' : traceback.format_exc(),
                        'exception_class' : e.__class__.__name__
                        },
                    'location' : (((None,None),(None,None)),)
                }
                results[analyzer_name] = {'issues' :  [issue]}

        results['analysis_time'] = dict(analysis_time)

        return results

def apply_filter(filename,patterns):
    return reduce(lambda x,y:x or y,[True if re.search(pattern,filename) 
                                     else False for pattern in patterns],False)

