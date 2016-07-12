from .analyzer import PyFlakesAnalyzer
from .issues_data import issues_data

analyzers = {
    'pyflakes' :
        {
            'title' : 'PyFlakes',
            'name' : 'pyflakes',
            'class' : PyFlakesAnalyzer,
            'language' : 'python',
            'issues_data' : issues_data
        },
}
