from .analyzer import FormatAnalyzer
from .issues_data import issues_data

analyzers = {
    'metrics' :
        {
            'title' : 'Code Metrics',
            'class' : FormatAnalyzer,
            'language' : 'python',
            'issues_data' : issues_data,
        },
}
