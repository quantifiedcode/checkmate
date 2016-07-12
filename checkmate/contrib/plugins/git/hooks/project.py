from ..helpers import Git
from ..models import GitSnapshot,GitBranch
import logging

logger = logging.getLogger(__name__)

def initialize_project(settings, project):
    project.properties['git'] = Git(project)

def before_project_save(settings, project):
    pass

def before_project_reset(settings, project):
    backend = project.backend
    branches = backend.filter(GitBranch,{'project' : project})
    logger.info("Deleting %d branches" % len(branches))
    branches.delete()
    snapshots = backend.filter(GitSnapshot,{'snapshot.project' : project})
    logger.info("Deleting %d snapshots" % len(snapshots))
    snapshots.delete()
	#do not call commit here, as this is done above
