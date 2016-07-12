from checkmate.lib.stats.helpers import directory_splitter
from checkmate.lib.models import (Project,
                                  Snapshot,
                                  DiskSnapshot,
                                  FileRevision,
                                  Issue)

"""
Default settings values
"""

from collections import defaultdict

hooks = defaultdict(list)

language_patterns = { 'python':
                        {
                            'name' : 'Python',
                            'patterns' : [u'\.py$',u'\.pyw$'],
                        },
                      'javascript' : {
                            'name' : 'Javascript',
                            'patterns' : [u'\.js$'],
                      },
                      'php' : {
                            'name' : 'PHP',
                            'patterns' : [u'\.php$'],
                      },
                      'ruby' : {
                            'name' : 'Ruby',
                            'patterns' : [u'\.rb'],
                      },
                    }

analyzers = {}

commands = {
    'alembic' : 'checkmate.management.commands.alembic.Command',
    'init' : 'checkmate.management.commands.init.Command',
    'analyze' : 'checkmate.management.commands.analyze.Command',
    'reset' : 'checkmate.management.commands.reset.Command',
    'shell' : 'checkmate.management.commands.shell.Command',
    'summary' : 'checkmate.management.commands.summary.Command',
    'snapshots' : 'checkmate.management.commands.snapshots.Command',
    'issues' : 'checkmate.management.commands.issues.Command',
    'props' : {
        'get' : 'checkmate.management.commands.props.get.Command',
        'set' : 'checkmate.management.commands.props.set.Command',
        'delete' : 'checkmate.management.commands.props.delete.Command'
    }
}

models = {
    'Project' : Project,
    'Snapshot' : Snapshot,
    'DiskSnapshot' : DiskSnapshot,
    'FileRevision' : FileRevision,
    'Issue' : Issue,
}

plugins = {
           'pep8' : 'checkmate.contrib.plugins.python.pep8',
           'pylint' : 'checkmate.contrib.plugins.python.pylint',
           'pyflakes' : 'checkmate.contrib.plugins.python.pyflakes',
           'jshint' : 'checkmate.contrib.plugins.javascript.jshint',
           'metrics' : 'checkmate.contrib.plugins.python.metrics',
           'git' : 'checkmate.contrib.plugins.git'
           }

aggregators = {
    'directory' :
        {
            'mapper' : lambda file_revision:directory_splitter(file_revision['path'],include_filename=True)
        }
}

checkignore = """*/site-packages/*
*/dist-packages/*
*/build/*
*/eggs/*
*/migrations/*
*/alembic/versions/*
"""
