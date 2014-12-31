# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from checkmate.management.commands.base import BaseCommand
from checkmate.management.helpers import save_project_config

import sys
import os
import os.path
import json
import time
import uuid

class Command(BaseCommand):

    description = "Deletes a project variable"

    def run(self):
        if len(self.raw_args) < 1:
            sys.stderr.write("Usage: props del [name]\n")
            return -1
        propname = self.raw_args[0]
        if not hasattr(self.project,'props'):
            self.project.props = {}
        if propname in self.project.props:
            del self.project.props[propname]
        self.backend.save(self.project)
        self.backend.commit()
        return 0
