from .analyzer import Pep8Analyzer
from .issues_data import issues_data

analyzers = {
    'pep8' :
        {
            'title' : 'Pep-8',
            'class' : Pep8Analyzer,
            'language' : 'python',
            'issues_data' : issues_data,
        },
}
