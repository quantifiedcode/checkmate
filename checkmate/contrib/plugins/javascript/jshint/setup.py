from .analyzer import JSHintAnalyzer
from .issues_data import issues_data

analyzers = {
    'jshint' :
        {
            'title' : 'JSHint',
            'class' : JSHintAnalyzer,
            'language' : 'javascript',
            'issues_data' : issues_data,
        },
}
