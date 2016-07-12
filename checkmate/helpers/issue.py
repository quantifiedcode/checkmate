from collections import defaultdict
from checkmate.lib.stats.mapreduce import MapReducer

class IssuesMapReducer(MapReducer):

    def __init__(self,aggregators,count_column = 'count',group_by = ['language','analyzer','code']):
        self.aggregators = aggregators
        self.count_column = count_column
        self.group_by = group_by

    def map(self,item):
        for group in self.group_by:
            if not group in item:
                return []
        return [(key,item) for aggregator in self.aggregators 
                for key in aggregator(item)]

    def reduce(self,key,items):
        grouped_issues ={}

        if self.group_by:
            for item in items:
                invalid_item = False
                current_dict = grouped_issues
                for group in self.group_by[:-1]:
                    if not group in item:
                        invalid_item = True
                        break
                    if not item[group] in current_dict:
                        current_dict[item[group]] = {}
                    current_dict = current_dict[item[group]]
                if not self.group_by[-1] in item:
                    invalid_item = True
                if invalid_item:
                    continue
                if not item[self.group_by[-1]] in current_dict:
                    current_dict[item[self.group_by[-1]]]= [0,0]
                cd = current_dict[item[self.group_by[-1]]]
                cd[0]+=1
                cd[1]+=item[self.count_column]
            return grouped_issues
        else:
            issues_sum = [0,0]
            for item in items:
                issues_sum[0]+=1
                issues_sum[1]+=item[self.count_column]
            return issues_sum

def group_issues_by_fingerprint(issues):
    """
    Groups issues by fingerprint. Grouping is done by issue code in addition.
    IMPORTANT: It is assumed that all issues come from the SAME analyzer.
    """
    issues_by_fingerprint = defaultdict(list)
    for issue in issues:
        if not 'fingerprint' in issue:
            raise AttributeError("No fingerprint defined for issue with analyzer %s and code %s!" %
                (issue.get('analyzer','(undefined)'),issue['code']))
        fp_code = "%s:%s" % (issue['fingerprint'],issue['code'])
        if fp_code in issues_by_fingerprint:
            grouped_issue = issues_by_fingerprint[fp_code]
        else:
            grouped_issue = issue.copy()
            grouped_issue['occurrences'] = []
            if 'location' in grouped_issue:
                del grouped_issue['location']
            issues_by_fingerprint[fp_code] = grouped_issue

        locations = issue.get('location',[])
        if locations:
            for i,start_stop in enumerate(locations):

                occurrence = {
                    'from_row' : None,
                    'to_row' : None,
                    'from_column' : None,
                    'to_column' : None,
                    'sequence' : i
                }

                grouped_issue['occurrences'].append(occurrence)

                if not isinstance(start_stop,(list,tuple)) or not len(start_stop) == 2:
                    continue

                start,stop = start_stop

                if isinstance(start,(list,tuple)) and len(start) == 2:
                    occurrence['from_row'] = start[0]
                    occurrence['from_column'] = start[1]

                if isinstance(stop,(list,tuple)) and len(stop) == 2:
                    occurrence['to_row'] = stop[0]
                    occurrence['to_column'] = stop[1]

            grouped_issue['occurrences'] = sorted(grouped_issue['occurrences'],key = lambda x: (x['from_row'],x['from_column']))

    return issues_by_fingerprint.values()

