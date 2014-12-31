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

from base import BaseCommand

from collections import defaultdict

import sys
import os
import random
import os.path
import copy
import json
import time
import pprint
import hashlib
import logging

logger = logging.getLogger(__name__)

from checkmate.management.helpers import filter_filenames_by_checkignore
from checkmate.lib.code import CodeEnvironment


def diff_objects(objects_a,objects_b,key,comparator,with_unchanged = False):
    """
    Returns a "diff" between two lists of objects.

    :param key: The key that identifies objects with identical location in each set, 
                such as files with the same path or code objects with the same URL.
    :param comparator: Comparison functions that decides if two objects are identical.
    """
    objects_a_by_key = dict([(key(obj),obj) for obj in objects_a if key(obj)])
    objects_b_by_key = dict([(key(obj),obj) for obj in objects_b if key(obj)])

    added_objects = [obj for key,obj in objects_b_by_key.items() if key not in objects_a_by_key]
    deleted_objects = [obj for key,obj in objects_a_by_key.items() if key not in objects_b_by_key]

    joint_keys = [key for key in objects_a_by_key if key in objects_b_by_key]

    modified_objects = [objects_b_by_key[key] for key in joint_keys if
                            comparator(objects_a_by_key[key],objects_b_by_key[key]) != 0
                       ]

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

class Command(BaseCommand):

    def diff_snapshots(self,code_environment,snapshot_a,snapshot_b):
 
        diff = {'snapshot_a' : snapshot_a,'snapshot_b' : snapshot_b,'project' : self.project}

        def code_object_key(code_object):
            key = os.path.join(code_object.module_url,code_object.tree_url)
            return key

        def code_object_comparator(code_object_a,code_object_b):
            return code_object_b.hash-code_object_a.hash

        def file_revision_key(file_revision):
            return file_revision.path

        def file_revision_comparator(file_revision_a,file_revision_b):
            res = 0 if file_revision_a.fr_pk == file_revision_b.fr_pk else -1
            return res

        def issue_key(issue):
            try:
                return issue.file_revision.path+":"+issue.analyzer+\
                       ":"+issue.code+":"+issue.fingerprint
            except AttributeError:
                return issue.file_revision.path+":"+issue.analyzer+":"+issue.code

        def issue_comparator(issue_a,issue_b):
            if issue_key(issue_a) == issue_key(issue_b):
                return 0
            return -1

        file_revisions_a = snapshot_a.get_file_revisions(self.backend)
        file_revisions_b = snapshot_b.get_file_revisions(self.backend)

        diff['file_revisions'] = diff_objects(file_revisions_a,
                                              file_revisions_b,
                                              file_revision_key,
                                              file_revision_comparator)

        #We just generate code objects and issues 
        #for the modified file revisions, to save time when diffing.

        logger.info("Generating list of modified file revisions...")
        modified_file_revisions_by_path = {}
        for fr_type in ('modified','added','deleted'):
            for fr in diff['file_revisions'][fr_type]:
                if not fr.path in modified_file_revisions_by_path:
                    modified_file_revisions_by_path[fr.path] = fr

        logger.info("Generating list of modified issues...")

        modified_file_revisions_a = [fr for fr in file_revisions_a 
                                     if fr.path in modified_file_revisions_by_path]
        modified_file_revisions_b = [fr for fr in file_revisions_b 
                                     if fr.path in modified_file_revisions_by_path]

        issues_a = self.backend.filter(self.project.Issue,
                                     {'project.pk' : self.project.pk,
                                        'file_revision.pk' : {'$in' : [fr.pk 
                                            for fr in modified_file_revisions_a]}
                                     })
        issues_b = self.backend.filter(self.project.Issue,
                                       {'project.pk' : self.project.pk,
                                        'file_revision.pk' : {'$in' : [fr.pk 
                                            for fr in modified_file_revisions_b]}
                                        })

        logger.info("Diffing issues (%d in A, %d in B)" % (len(issues_a),len(issues_b)))
        diff['issues'] = diff_objects(issues_a,issues_b,issue_key,issue_comparator)

        logger.info("Diffing summary...")
        diff['summary'] = code_environment.diff_summaries(snapshot_a,snapshot_b)

        diff['summary']['issues'] = {}
        diff['summary']['file_revisions'] = {}

        logger.info("Summarizing diffed file revisions and issues...")
        for key in ('added','modified','deleted'):
            diff['summary']['file_revisions'][key] = len(diff['file_revisions'][key])
            diff['summary']['issues'][key] = code_environment.summarize_issues(diff['issues'][key])

        #Add summary to snapshot_b, so that it can be displayed without fetching the diff object

        return diff

    def get_settings(self):
        settings = {}
        if 'settings' in self.project:
            settings.update(self.project.settings)
        settings_filename = os.path.join(self.project.path,'.checkmate.yml')
        if os.path.exists(settings_filename):
            with open(settings_filename,"r") as settings_file:
                settings = parse_settings(settings_file.read())
        if 'settings' in self.opts:
            settings.update(self.opts['settings'])
        return settings

    def run(self):

        settings = self.get_settings()

        if 'ignore' in settings:
            checkignore = settings['ignore']
        else:
            checkignore = []

        checkignore_filter = lambda filenames : filter_filenames_by_checkignore(filenames,
                                                                                checkignore)

        logger.info("Getting file revisions...")
        file_revisions = self.project.get_disk_file_revisions(file_filters = [checkignore_filter],
                                                              path_filters = [checkignore_filter])
        logger.info("%d file revisions" % len(file_revisions))

        snapshot = self.project.DiskSnapshot({'created_at' : time.time()})
 
        try:
            code_environment = CodeEnvironment(file_revisions,
                                               settings = settings)
            self.analyze_snapshot(snapshot,
                                  code_environment,
                                  save_if_empty = False)
        except KeyboardInterrupt:
            raise

    def generate_diffs(self,code_environment,snapshot_pairs):

        diffs = []

        logger.info("Generating diffs beween %d snapshot pairs..." % len(snapshot_pairs))

        for snapshot_a,snapshot_b in snapshot_pairs:
            logger.info("Generating a diff between snapshots %s and %s" % (snapshot_a.pk,
                                                                           snapshot_b.pk))
            diff = self.diff_snapshots(code_environment,snapshot_a,snapshot_b)
            diffs.append(diff)

        return diffs

    def fingerprint_issues(self,file_revision,issues):
        content = file_revision.get_file_content()
        lines = content.split("\n")
        for issue in issues:
            lines = "\n".join([line for loc in issue.location 
                                    for line in lines[loc[0][0]:loc[1][0]]])
            sha = hashlib.sha1()
            sha.update(lines)
            issue.fingerprint = sha.hexdigest()

    def annotate_file_revisions(self,snapshot,file_revisions):
        """
        We convert various items in the file revision to documents, 
        so that we can easily search and retrieve them...
        """

        annotations = defaultdict(list)

        def group_issues_by_code(issues):
            """
            We group the issues by code to avoid generating 100s of issues per file...
            """
            issues_for_code = {}
            for issue in issues:
                if not issue['code'] in issues_for_code:
                    issues_for_code[issue['code']] = copy.deepcopy(issue)
                    code_issue = issues_for_code[issue['code']]

                    if 'location' in code_issue:
                        del code_issue['location']
                    if 'data' in code_issue:
                        del code_issue['data']

                    code_issue['occurences'] = []

                code_issue = issues_for_code[issue['code']]
                issue_data = {}
                for key in ('location','data'):
                    if key in issue:
                        issue_data[key] = issue[key]
                code_issue['occurences'].append(issue_data)
            return issues_for_code.values()

        for file_revision in file_revisions:
            for analyzer_name,results in file_revision.results.items():

                if 'issues' in results:
                    if len(results['issues']) > 1000:
                        results['issues'] = [
                            {
                                'code' : 'TooManyIssues',
                                'data' : {
                                    'analyzer' : analyzer_name,
                                    'count' : len(results['issues'])
                                    },
                                'occurences' : []
                            }
                        ]

                    documents = []
                    grouped_issues = group_issues_by_code(results['issues'])

                    for issue in grouped_issues:

                        document = self.project.Issue(issue)
                        document.project = self.project
                        document.file_revision = file_revision
                        document.analyzer = analyzer_name
                        documents.append(document)

                    annotations['issues'].extend(documents)
                    del results['issues']

        return annotations

    def analyze_snapshot(self,snapshot,code_environment,save_if_empty = False):

        logger.info("Analyzing snapshot...")

        file_revisions = code_environment.file_revisions
        file_revisions_by_pk = dict([(fr.fr_pk,fr) for fr in file_revisions])

        filtered_file_revisions = code_environment.filter_file_revisions(file_revisions)
        filtered_file_revisions_by_pk = dict([(fr.fr_pk,fr) for fr in filtered_file_revisions])

        excluded_file_revisions = [file_revisions_by_pk[pk]
                                    for pk in file_revisions_by_pk.keys()
                                    if not pk in filtered_file_revisions_by_pk
                                  ]
        logger.info("Excluding %d file revisions:" % len(excluded_file_revisions))

        file_revisions = filtered_file_revisions
        file_revisions_by_pk = filtered_file_revisions_by_pk

        max_file_revisions = 300
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

            logger.error("Too many file revisions (%d) in snapshot, truncating at %d" % 
                         (len(file_revisions),max_file_revisions))
            file_revisions_by_pk = dict(sorted(file_revisions_by_pk.items(),
                                               key = lambda x:x[0])[:max_file_revisions])
            file_revisions = file_revisions_by_pk.values()


        existing_file_revisions = list(self.backend.filter(snapshot.FileRevision,{
                'project.pk' : self.project.pk,
                'fr_pk' : {'$in' : file_revisions_by_pk.keys()}
                }))
        existing_file_revisions_by_pk = dict([(fr.fr_pk,fr) for fr in existing_file_revisions])
        new_file_revisions = [file_revision for file_revision in file_revisions
                                if not file_revision.fr_pk in existing_file_revisions_by_pk]

        file_revisions_dict = {}

        for file_revision in existing_file_revisions+new_file_revisions:
            file_revisions_dict[file_revision.path] = file_revision

        logger.info("Analyzing %d new file revisions (%d are already analyzed)" % (
                len(new_file_revisions),
                len(existing_file_revisions)
                ))
        i = 0

        snapshot_issues = list(self.backend.filter(self.project.Issue,
                            {'file_revision.pk' : {'$in' : [fr.pk 
                                for fr in existing_file_revisions]  }
                            }))
        logger.info("Found %d existing issues..." % len(snapshot_issues))

        code_environment.env['snapshot'] = snapshot
        try:
            while i < len(new_file_revisions):

                j = i+10 if i+10 < len(new_file_revisions) else len(new_file_revisions)

                logger.info("Analyzing and saving: %d - %d (%d remaining)" % 
                    (i, j, len(new_file_revisions) - i ))

                file_revisions_slice = new_file_revisions[i:j]
                analyzed_file_revisions = code_environment.analyze_file_revisions(file_revisions_slice)

                logger.info("Annotating and saving file revisions...")

                annotations = self.annotate_file_revisions(snapshot,analyzed_file_revisions)

                if 'issues' in annotations:
                    snapshot_issues.extend(annotations['issues'])

                for file_revision in analyzed_file_revisions:
                    self.backend.save(file_revision)
                self.backend.commit()

                for issue in annotations['issues']:
                    self.backend.save(issue)

                self.backend.commit()

                i+=10

            logger.info("Summarizing file revisions...")
            snapshot.summary = code_environment.summarize(file_revisions_dict.values())
            logger.info("Summarizing issues...")
            snapshot.issues_summary = code_environment.summarize_issues(snapshot_issues)
        finally:
            del code_environment.env['snapshot']

        snapshot.analyzed = True
        snapshot.project = self.project

        logger.info("Saving snapshot...")

        snapshot.file_revisions = [fr.pk for fr in file_revisions_dict.values()]

        self.backend.save(snapshot)
        self.backend.commit()

        logger.info("Done analyzing snapshot %s" % snapshot.pk)

        return snapshot
