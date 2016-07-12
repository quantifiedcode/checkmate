# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from checkmate.management.commands.analyze import Command as AnalyzeCommand
from ..models import GithubProject

import time
import datetime
import traceback
import logging

from checkmate.lib.code import CodeEnvironment

logger = logging.getLogger(__name__)

class Command(AnalyzeCommand):

    options = AnalyzeCommand.options + []

    def run(self):

        if not hasattr(self.project,'github'):
            logger.error("Not a Github project!")
            return -1
