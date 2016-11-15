from .commands.analyze import Command as AnalyzeCommand
from .commands.diff import Command as DiffCommand
from .commands.update_stats import Command as UpdateStatsCommand
from .commands.init import Command as InitCommand

from .models import GitSnapshot, GitBranch, GitRepository
from .hooks.project import before_project_save,before_project_reset

commands = {
    'init' : InitCommand,
    'analyze' : AnalyzeCommand,
    'diff' : DiffCommand,
    'update_stats' : UpdateStatsCommand
}

models = {
    'GitSnapshot' : GitSnapshot,
    'GitBranch' : GitBranch,
    'GitRepository' : GitRepository,
}

hooks = {
    'project.save.before' : before_project_save,
    'project.reset.before' : before_project_reset
}

top_level_commands = {}
