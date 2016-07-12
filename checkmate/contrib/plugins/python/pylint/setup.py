from .analyzer import PyLintAnalyzer
from .issues_data import issues_data

analyzers = {
    'pylint' :
        {
            'name' : 'pylint',
            'title' : 'PyLint',
            'class' : PyLintAnalyzer,
            'language' : 'python',
            'issues_data' : issues_data,
        },
}
