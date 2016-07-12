# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import defaultdict
from checkmate.lib.analysis.base import BaseAnalyzer

import logging

logger = logging.getLogger(__name__)

class FormatAnalyzer(BaseAnalyzer):

    def diff_summary(self,summary_a,summary_b):

        return {
                'd_number_of_lines' : summary_b['total_number_of_lines']-summary_a['total_number_of_lines'],
                'd_number_of_characters' : summary_b['total_number_of_characters']-summary_a['total_number_of_characters'],
               }

    def summarize(self,items):

        stats = defaultdict(lambda : {})

        stats['total_number_of_lines'] = 0
        stats['total_number_of_characters'] = 0
        cnt = 0

        for item in [item['stats'] for item in items if 'stats' in item]:
            if 'number_of_lines' in item and 'number_of_characters' in item:
                stats['total_number_of_lines'] += item['number_of_lines']
                stats['total_number_of_characters'] += item['number_of_characters']
                cnt += 1

        if cnt:
            stats['average_number_of_lines'] = stats['total_number_of_lines'] / float(cnt)
            stats['average_number_of_characters'] = stats['total_number_of_characters'] / float(cnt)

        stats['number_of_files'] = cnt

        return dict(stats)

    def analyze(self,file_revision):

        stats = {}
        issues = []

        try:
            file_content = file_revision.get_file_content()
            stats['number_of_lines'] = len(file_content.decode("utf-8","ignore").split("\n"))
            stats['number_of_characters'] = len(file_content.decode("utf-8","ignore"))
        except KeyboardInterrupt:
            raise
        except:
            logger.warning("Cannot read source file: %s" % file_revision.path)
            pass
        return {
            'stats' : stats,
            'issues' : issues,
        }
