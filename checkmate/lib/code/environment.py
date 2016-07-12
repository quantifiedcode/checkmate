# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import re
import time
import traceback
import logging
import six
import copy
import hashlib

from checkmate.helpers.issue import group_issues_by_fingerprint
from checkmate.management.helpers import (filter_filenames_by_analyzers,
                                          filter_filenames_by_checkignore)
from checkmate.helpers.hashing import Hasher
from checkmate.lib.analysis.base import BaseAnalyzer
from checkmate.lib.models import (Issue,
                                  IssueOccurrence,
                                  Diff,
                                  Snapshot,
                                  FileRevision,
                                  DiffFileRevision,
                                  DiffIssueOccurrence)

from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalysisTimeAnalyzer(BaseAnalyzer):

    def summarize(self,items):

        stats = defaultdict(lambda : 0.0)

        for item in items:
            for analyzer,duration in item.items():
                stats[analyzer]+=duration

        return dict(stats)

def apply_filter(filename,patterns):
    return reduce(lambda x,y:x or y,[True if re.search(pattern,filename)
                                     else False for pattern in patterns],False)

def diff_objects(objects_a,objects_b,key,comparator = None,with_unchanged = False):
    """
    Returns a "diff" between two lists of objects.

    :param key: The key that identifies objects with identical location in each set,
                such as files with the same path or code objects with the same URL.
    :param comparator: Comparison functions that decides if two objects are identical.
    """

    objects_by_key = {'a' :defaultdict(list),
                      'b' : defaultdict(list)}

    for name,objects in ('a',objects_a),('b',objects_b):
        d = objects_by_key[name]
        for obj in objects:
            d[key(obj)].append(obj)

    added_objects = [obj for key,objs in objects_by_key['b'].items()
                     if key not in objects_by_key['a'] for obj in objs]

    deleted_objects = [obj for key,objs in objects_by_key['a'].items()
                       if key not in objects_by_key['b'] for obj in objs]

    joint_keys = [key for key in objects_by_key['a']
                  if key in objects_by_key['b']]

    modified_objects = []

    #we go through the keys that exist in both object sets
    for key in joint_keys:
        objects_a = objects_by_key['a'][key]
        objects_b = objects_by_key['b'][key]

        if len(objects_a) > 1 or len(objects_b) > 1:

            #this is an ambiguous situation: we have more than one object for the same
            #key, so we have to decide which ones have been added or not
            #we try to remove identical objects from the set

            objects_a_copy = objects_a[:]
            objects_b_copy = objects_b[:]

            #for the next step, we need a comparator
            if comparator:
                #we iterate through the list and try to find different objects...
                for obj_a in objects_a:
                    for obj_b in objects_b_copy:
                        if comparator(obj_a,obj_b) == 0:
                            #these objects are identical, we remove them from both sets...
                            objects_a_copy.remove(obj_a)
                            objects_b_copy.remove(obj_b)
                            break

            #here we cannot distinguish objects...
            if len(objects_b_copy) > len(objects_a_copy):
                #we arbitrarily mark the last objects in objects_b as added
                added_objects.extend(objects_b_copy[len(objects_a_copy):])
            elif len(objects_a_copy) > len(objects_b_copy):
                #we arbitrarily mark the last objects in objects_a as deleted
                deleted_objects.extend(objects_a_copy[len(objects_b_copy):])
        else:
            if comparator and comparator(objects_a[0],objects_b[0]) != 0:
                #these objects are different
                modified_objects.append(objects_a[0])

    result = {
        'added' : added_objects,
        'deleted' : deleted_objects,
        'modified' : modified_objects,
    }

    if with_unchanged:
        unchanged_objects = [objects_b_by_key[key]
                             for key in joint_keys
                             if not objects_b_by_key[key] in modified_objects]
        result['unchanged'] = unchanged_objects

    return result

def file_revision_key(file_revision):
    return file_revision.path

def file_revision_comparator(file_revision_a,file_revision_b):
    return 0 if file_revision_a.hash == file_revision_b.hash else -1

def issue_occurrence_key(issue_occurrence):
    try:
        return issue_occurrence.file_revision.path+":"+issue_occurrence.issue.analyzer+\
               ":"+issue_occurrence.issue.code+":"+issue_occurrence.issue.fingerprint
    except AttributeError:
        return issue_occurrence.file_revision.path+":"+issue_occurrence.issue.analyzer+":"+issue_occurrence.issue.code

def issue_occurrence_comparator(issue_occurrence_a,issue_occurrence_b):
    if issue_occurrence_key(issue_occurrence_a) != issue_occurrence_key(issue_occurrence_b):
        return -1
    if issue_occurrence_a.from_row != issue_occurrence_b.from_row or\
       issue_occurrence_a.to_row != issue_occurrence_b.to_row or\
       issue_occurrence_a.from_column != issue_occurrence_b.from_column or\
       issue_occurrence_a.to_column != issue_occurrence_b.to_column:
       return -1

    return 0

class CodeEnvironment(object):

    """
    Represents the full code environment of the project, including all code files.

    Responsibilities of the code environment:

    -Manage a list of file revisions
    -Manage a list of analyzers and aggregators
    -Manage project parameters that passed on to the analyzers
    """

    def __init__(self,
                 project,
                 global_settings,
                 project_settings,
                 raise_on_analysis_error = False,
                 env = None,
                 file_revisions = None,
                 ):
        self.project = project
        #global settings dictionary
        self.global_settings = global_settings
        self.project_settings = project_settings
        self.raise_on_analysis_error = raise_on_analysis_error
        self._env = env if env is not None else {}
        self._file_revisions = file_revisions

        self._active_analyzers = None
        self._active_aggregators = None
        self._analyzer_cache = {}

    def create_analysis_error(self, exception_str, location = None):
        issue_doc = {
            'code' : 'AnalysisError',
            'data' : {
                'exception' : exception_str
            },
            'location' : location,
            'fingerprint' : hashlib.sha256(exception_str).hexdigest(),
        }
        return issue_doc

    @property
    def file_revisions(self):
        return self._file_revisions

    @file_revisions.setter
    def file_revisions(self, file_revisions):
        self._file_revisions = file_revisions
        #we reset the analyzers and aggregators, as they depend
        #on the file revision information...
        self._active_analyzers = None
        self._active_aggregators = None

    @property
    def env(self):
        return self._env

    @property
    def analyzers(self):
        if self._active_analyzers is None:
            self._active_analyzers = self.get_active_analyzers()
        return self._active_analyzers

    @property
    def aggregators(self):
        if self._active_aggregators is None:
            self._active_aggregators = self.get_active_aggregators()
        return self._active_aggregators

    def get_language(self,file_revision):
        for language,language_pattern in self.global_settings.language_patterns.items():
            if 'patterns' in language_pattern and \
                apply_filter(file_revision['path'],language_pattern['patterns']):
                return language
        return None

    def filter_file_revisions(self,file_revisions):
        analyzer_filter = lambda filenames : filter_filenames_by_analyzers(filenames,
                                                                           self.global_settings.analyzers.values(),
                                                                           self.global_settings.language_patterns)

        filters = [analyzer_filter]

        if 'ignore' in self.project_settings:
            checkignore = self.project_settings['ignore']
            filters.append(lambda filenames : filter_filenames_by_checkignore(filenames,checkignore))

        file_revisions_by_path = {fr.path : fr for fr in file_revisions}
        filtered_paths = file_revisions_by_path.keys()

        for path_filter in filters:
            filtered_paths = path_filter(filtered_paths)

        return [file_revisions_by_path[path] for path in filtered_paths]

    def _get_active_objects(self, objs, disabled_by_default=False, obj_type='analyzers'):
        active_objs = {}
        project_settings = self.project_settings
        project_obj_settings = project_settings.get(obj_type,{})
        for name,params in objs.items():
            if 'enable' in project_obj_settings and not name in project_obj_settings['enable']:
                continue
            if 'disable' in project_obj_settings and name in project_obj_settings['disable']:
                continue
            if not name in project_obj_settings and disabled_by_default:
                continue
            obj_settings = params.copy()
            if not 'settings' in obj_settings:
                obj_settings['settings'] = {}
            project_obj_settings = project_obj_settings.get(name,{})
            if 'settings' in project_obj_settings:
                obj_settings['settings'].update(project_obj_settings['settings'])
            active_objs[name] = obj_settings
        return active_objs

    def get_active_aggregators(self, disabled_by_default=False):
        return self._get_active_objects(self.global_settings.aggregators, disabled_by_default=disabled_by_default, obj_type='aggregators')

    def get_active_analyzers(self, disabled_by_default=False):
        return self._get_active_objects(self.global_settings.analyzers, disabled_by_default=disabled_by_default, obj_type='analyzers')

    def init_analyzer(self,name,parameters):
        class_str = parameters['class']

        if class_str in self._analyzer_cache:
            return self._analyzer_cache[class_str]

        if isinstance(class_str,six.string_types):
            (module_name,separator,class_name) = class_str.rpartition(u".")
            module = __import__(module_name,globals(),locals(),[str(class_name)],-1)
            analyzer_class = getattr(module,class_name)
        else:
            analyzer_class = class_str

        try:
            analyzer = analyzer_class(self,
                                      issue_classes = parameters.get('issue_classes'),
                                      settings = parameters.get('settings'),
                                      ignore = parameters.get('ignore')
                                      )
        except:
            logger.error("Cannot initialize analyzer {}".format(name))
            logger.debug(traceback.format_exc())
            analyzer = None
        self._analyzer_cache[class_str] = analyzer
        return analyzer

    def diff_snapshots(self,snapshot_a,snapshot_b,save = True, diff=None):

        """
        Returns a list of
        """

        file_revisions_a = snapshot_a.file_revisions
        file_revisions_b = snapshot_b.file_revisions

        file_revisions_diff = diff_objects(file_revisions_a,
                                           file_revisions_b,
                                           file_revision_key,
                                           file_revision_comparator)

        #We just generate code objects and issues
        #for the modified file revisions, to save time when diffing.

        logger.info("Generating list of modified file revisions...")
        modified_file_revisions_by_path = {}
        for fr_type in ('modified','added','deleted'):
            for fr in file_revisions_diff[fr_type]:
                if not fr.path in modified_file_revisions_by_path:
                    modified_file_revisions_by_path[fr.path] = fr

        logger.info("Generating list of modified issues...")

        modified_file_revisions_a = [fr for fr in file_revisions_a
                                     if fr.path in modified_file_revisions_by_path]
        modified_file_revisions_b = [fr for fr in file_revisions_b
                                     if fr.path in modified_file_revisions_by_path]

        if modified_file_revisions_a:
            #to do: check the file revisions chunk-wise to avoid DB query errors
            issue_occurrences_a = self.project.backend.filter(IssueOccurrence,
                                         {
                                            'file_revision' : {'$in' : modified_file_revisions_a}
                                         },
                                      include = ('file_revision','issue'))
        else:
            issue_occurrences_a = []

        if modified_file_revisions_b:
            #to do: check the file revisions chunk-wise to avoid DB query errors
            issue_occurrences_b = self.project.backend.filter(IssueOccurrence,
                                           {
                                            'file_revision' : {'$in' : modified_file_revisions_b}
                                            },
                                      include = ('file_revision','issue'))
        else:
            issue_occurrences_b = []

        logger.info("Diffing issues (%d in A, %d in B)" % (len(issue_occurrences_a),
                                                           len(issue_occurrences_b)))


        issue_occurrences_diff = diff_objects(issue_occurrences_a,
                                              issue_occurrences_b,
                                              issue_occurrence_key,
                                              issue_occurrence_comparator)

        logger.info("Diffing summary...")
        summary_diff = self.diff_summaries(snapshot_a,snapshot_b)

        if diff is None:
            diff = Diff({'summary' : summary_diff,
                        'snapshot_a' : snapshot_a,
                        'project' : self.project,
                        'configuration' : self.project.configuration,
                        'snapshot_b' : snapshot_b})
            #we generate the hash value for this diff
            hasher = Hasher()
            hasher.add(diff.snapshot_a.hash)
            hasher.add(diff.snapshot_b.hash)
            diff.hash = hasher.digest.hexdigest()
        elif save:
            with self.project.backend.transaction():
                self.project.backend.filter(DiffFileRevision,{'diff' : diff}).delete()
                self.project.backend.filter(DiffIssueOccurrence,{'diff' : diff}).delete()
        if save:
            with self.project.backend.transaction():
                self.project.backend.save(diff)

        diff_file_revisions = []

        with self.project.backend.transaction():
            for key,file_revisions in file_revisions_diff.items():
                for file_revision in file_revisions:
                    hasher = Hasher()
                    hasher.add(file_revision.hash)
                    hasher.add(diff.hash)
                    hasher.add(key)
                    diff_file_revision = DiffFileRevision({
                                            'diff' : diff,
                                            'file_revision' : file_revision,
                                            'hash' : hasher.digest.hexdigest(),
                                            'key' : key})
                    if save:
                        self.project.backend.save(diff_file_revision)
                    diff_file_revisions.append(diff_file_revision)

        diff_issue_occurrences = []
        mapping = {'deleted' : 'fixed','added' : 'added'}
        with self.project.backend.transaction():
            for key,issue_occurrences in issue_occurrences_diff.items():
                if not key in mapping:
                    continue
                for issue_occurrence in issue_occurrences:
                    hasher = Hasher()
                    hasher.add(issue_occurrence.hash)
                    hasher.add(diff.hash)
                    hasher.add(mapping[key])
                    diff_issue_occurrence = DiffIssueOccurrence({
                            'diff' : diff,
                            'hash' : hasher.digest.hexdigest(),
                            'issue_occurrence' : issue_occurrence,
                            'key' : mapping[key]
                        })
                    if save:
                        self.project.backend.save(diff_issue_occurrence)
                    diff_issue_occurrences.append(diff_issue_occurrence)

        return diff,diff_file_revisions,diff_issue_occurrences

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
                if analyzer is None:
                    continue

                for key in language_summary_a[analyzer_name]:
                    if not key in language_summary_b[analyzer_name]:
                        continue
                    result = analyzer.diff_summary(language_summary_a[analyzer_name][key],
                                                   language_summary_b[analyzer_name][key]
                                                  )
                    if result:
                        summary[language][analyzer_name][key] = result

        return summary

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
                    analyzer = self.init_analyzer(analyzer_name,analyzer_params)
                    if analyzer is None:
                        continue
                    for key in file_revisions_by_key:
                        try:
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
                            traceback.print_exc()
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
                if analyzer is None:
                    continue
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
                issue = self.create_analysis_error('An exception occurred during the analysis of this file.')
                logger.error(traceback.format_exc())
                results[analyzer_name] = {'issues' :  [issue]}

        results['analysis_time'] = dict(analysis_time)

        return results

    def analyze(self,file_revisions, save_if_empty = False, snapshot=None):

        """
        Handling dependencies:

        * First, genreate a list of file revisions for this snapshot
        * Then, check which ones of of them already exist
        * For the existing ones, check their dependencies
        * If any of the dependencies are outdated, add the dependent file revision to the analyze list

        How to handle hashes? Dependencies should be included in the hash sum.

        * Just load the files based on their SHA values
        * Check if dependencies match with the current set based on SHA values
        * If not, re-analyze the file revision
        * After analysis, calculate the hash value based on path, SHA and dependencies
        """

        logger.info("Analyzing code environment...")

        if snapshot is None:
            snapshot = Snapshot()
            snapshot.configuration = self.project.configuration

        file_revisions_by_pk = dict([(fr.hash,fr) for fr in file_revisions])

        filtered_file_revisions = self.filter_file_revisions(file_revisions)
        filtered_file_revisions_by_pk = dict([(fr.hash,fr) for fr in filtered_file_revisions])

        excluded_file_revisions = [file_revisions_by_pk[pk]
                                    for pk in file_revisions_by_pk.keys()
                                    if not pk in filtered_file_revisions_by_pk
                                  ]

        logger.info("Excluding %d file revisions" % len(excluded_file_revisions))

        file_revisions = filtered_file_revisions
        file_revisions_by_pk = filtered_file_revisions_by_pk

        max_file_revisions = 10000

        if len(file_revisions) > max_file_revisions:

            if not 'snapshot_issues' in snapshot:
                snapshot.snapshot_issues = []

            snapshot.snapshot_issues.append({
                    'code' : 'TooManyFileRevisions',
                    'data' : {
                            'count' : len(file_revisions),
                            'limit' : max_file_revisions
                        }
                    })

            logger.warning("Too many file revisions (%d) in snapshot, truncating at %d" %
                         (len(file_revisions),max_file_revisions))
            file_revisions_by_pk = dict(sorted(file_revisions_by_pk.items(),
                                               key = lambda x:x[0])[:max_file_revisions])
            file_revisions = file_revisions_by_pk.values()

        i = 0
        chunk_size = 50

        existing_file_revisions = []

        file_revisions_by_pk_keys = file_revisions_by_pk.keys()

        #we only check 50 keys at a time to not overload the database...
        while i < len(file_revisions_by_pk_keys):
            file_revisions_by_pk_chunk = file_revisions_by_pk_keys[i:i+chunk_size]
            if not file_revisions_by_pk_chunk:
                break
            existing_file_revisions.extend(list(self.project.backend.filter(FileRevision,{
                    'project' : self.project,
                    'hash' : {'$in' : file_revisions_by_pk_chunk}
                    })))
            i+=chunk_size

        existing_file_revisions_by_pk = dict([(fr.hash,fr) for fr in existing_file_revisions])
        new_file_revisions = [file_revision for file_revision in file_revisions
                                if not file_revision.hash in existing_file_revisions_by_pk]

        new_file_revisions = []

        for file_revision in file_revisions:
            if not file_revision.hash in existing_file_revisions_by_pk:
                file_revision.configuration = self.project.configuration
                new_file_revisions.append(file_revision)
            elif existing_file_revisions_by_pk[file_revision.hash].configuration != self.project.configuration:
                #we replace the pk and configuration values of the new file_revision object, so that
                #it will overwrite the old version...
                file_revision.pk = existing_file_revisions_by_pk[file_revision.hash].pk
                file_revision.configuration = self.project.configuration
                new_file_revisions.append(file_revision)

        file_revisions_dict = {}

        for file_revision in existing_file_revisions+new_file_revisions:
            file_revisions_dict[file_revision.path] = file_revision

        logger.info("Analyzing %d new file revisions (%d are already analyzed)" % (
                len(new_file_revisions),
                len(existing_file_revisions)
                ))
        i = 0

        #We set the project information in the snapshot.
        snapshot.project = self.project
        snapshot.file_revisions = file_revisions_dict.values()
        self.env['snapshot'] = snapshot

        try:
            while i < len(new_file_revisions):
                j = i+10 if i+10 < len(new_file_revisions) else len(new_file_revisions)
                logger.info("Analyzing and saving: %d - %d (%d remaining)" %
                    (i, j, len(new_file_revisions) - i ))
                file_revisions_slice = new_file_revisions[i:j]
                analyzed_file_revisions = self.analyze_file_revisions(file_revisions_slice)
                logger.info("Annotating and saving file revisions...")
                self.save_file_revisions(snapshot,analyzed_file_revisions)
                i+=10
            logger.info("Summarizing file revisions...")
            snapshot.summary = self.summarize(file_revisions_dict.values())
        finally:
            del self.env['snapshot']

        snapshot.analyzed = True

        logger.info("Saving snapshot...")

        with self.project.backend.transaction():
            self.project.backend.save(snapshot)

        logger.info("Done analyzing snapshot %s" % snapshot.pk)

        return snapshot

    def save_file_revisions(self,snapshot,file_revisions):
        """
        We convert various items in the file revision to documents,
        so that we can easily search and retrieve them...
        """

        annotations = defaultdict(list)

        for file_revision in file_revisions:
            issues_results = {}

            for analyzer_name,results in file_revision.results.items():

                if 'issues' in results:
                    issues_results[analyzer_name] = results['issues']
                    del results['issues']
                    if len(issues_results) > 1000:
                        issues_results[analyzer_name] = [{
                                'code' : 'TooManyIssues',
                                'analyzer' : analyzer_name,
                            }]

            with self.project.backend.transaction():
                self.project.backend.save(file_revision)

            def location_sorter(issue):
                if issue['location'] and issue['location'][0] and issue['location'][0][0]:
                    return issue['location'][0][0][0]
                return 0

            with self.project.backend.transaction():
                for analyzer_name,issues in issues_results.items():
                    grouped_issues = group_issues_by_fingerprint(issues)
                    for issue_dict in grouped_issues:

                        hasher = Hasher()
                        hasher.add(analyzer_name)
                        hasher.add(issue_dict['code'])
                        hasher.add(issue_dict['fingerprint'])
                        issue_dict['hash'] = hasher.digest.hexdigest()

                        try:
                            issue = self.project.backend.get(Issue,{'hash' : issue_dict['hash'],
                                                            'project' : self.project
                                                        })
                        except Issue.DoesNotExist:
                            d = issue_dict.copy()
                            d['analyzer'] = analyzer_name
                            if 'location' in d:
                                del d['location']
                            if 'occurrences' in d:
                                del d['occurrences']
                            issue = Issue(d)
                            issue.project = self.project
                            self.project.backend.save(issue)

                        for occurrence in issue_dict['occurrences']:
                            hasher = Hasher()
                            hasher.add(file_revision.hash)
                            hasher.add(issue.hash)
                            hasher.add(occurrence.get('from_row'))
                            hasher.add(occurrence.get('from_column'))
                            hasher.add(occurrence.get('to_row'))
                            hasher.add(occurrence.get('to_column'))
                            hasher.add(occurrence.get('sequence'))
                            occurrence['hash'] = hasher.digest.hexdigest()
                            occurrence = IssueOccurrence(occurrence)
                            occurrence.issue = issue
                            occurrence.file_revision = file_revision
                            self.project.backend.save(occurrence)
                            annotations['occurrences'].append(occurrence)

                        annotations['issues'].append(issue)

        return annotations
