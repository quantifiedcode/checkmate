from .commands.analyze import Command as AnalyzeCommand
from .commands.diff import Command as DiffCommand
from .commands.update_stats import Command as UpdateStatsCommand

from .models import GitSnapshot,GitBranch

commands = {
    'analyze' : AnalyzeCommand,
    'diff' : DiffCommand,
    'update_stats' : UpdateStatsCommand
}

models = {
    'GitSnapshot' : GitSnapshot,
    'GitBranch' : GitBranch,
}

from .hooks.project import initialize_project,before_project_save,before_project_reset

hooks = {
    'project.initialize' : initialize_project,
    'project.save.before' : before_project_save,
    'project.reset.before' : before_project_reset
}

top_level_commands = {}
